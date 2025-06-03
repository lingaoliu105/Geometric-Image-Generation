from abc import ABC, abstractmethod
import random
import re
from typing import Dict, List

import numpy as np

from generation_config import GenerationConfig, step_into_config_scope_decorator, step_out_config_scope

import generation_config
from shape_group import ShapeGroup


# to apply decorators written in base class to subclasses
def get_decorators_from_method(method):
    """尝试从方法中提取装饰器"""
    decorators = []

    # 如果是 functools.wraps 包装过的方法，递归提取
    current = method
    while hasattr(current, "__wrapped__"):
        decorators.append(current.__wrapped__)
        current = getattr(current, "__wrapped__", None)
    return decorators[::-1]  # 保持装饰器顺序


class AutoInheritDecoratorMeta(type):
    def __new__(cls, name, bases, attrs):
        # 创建新类之前，先处理方法
        for method_name, method in attrs.items():
            if callable(method) and not method_name.startswith("__"):
                
                
                # 收集所有父类中该方法的装饰器
                inherited_decorators = set()
                for base in reversed(bases):  # 从最远的祖先开始找
                    base_method = getattr(base, method_name, None)
                    if base_method and hasattr(base_method, "__wrapped__"):
                        inherited_decorators.update(
                            get_decorators_from_method(base_method)
                        )

                # 应用收集到的装饰器
                for decorator in inherited_decorators:
                    if decorator.__name__ == "step_into_config_scope" or decorator.__name__ == "step_out_config_scope":
                        method = decorator(method)
                attrs[method_name] = method

        return super().__new__(cls, name, bases, attrs)


class ImageGenerator(metaclass=AutoInheritDecoratorMeta):

    # @step_into_config_scope_decorator
    def __init__(self) -> None:
        self.shapes:ShapeGroup = ShapeGroup([[]])
        child_class_name = self.__class__.__name__
        if child_class_name.endswith("Generator"):
            child_class_name = child_class_name[:-9]

        def camel_to_snake(camel_str: str) -> str:
            """
            Convert a camel case string to snake case.
            
            :param camel_str: The camel case string to convert.
            :return: The snake case string.
            """
            # Use regular expression to insert underscores before uppercase letters and convert to lowercase
            snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
            return snake_str
        # Convert camel case to snake case
        snake_str = camel_to_snake(child_class_name)

        # Add _config suffix
        config_name = f"{snake_str}_config"
        try:
            self.distribution_dict = getattr(GenerationConfig,config_name)["sub_composition_distribution"]
        except (KeyError,TypeError) as e:
            self.distribution_dict  = {}
        if self.distribution_dict=={}:
            self.distribution_dict = {"simple":1.0}
    @abstractmethod
    @step_out_config_scope
    def generate(self)->ShapeGroup:
        pass

    @property
    def panel_center(self):
        return (self.panel_bottom_right+self.panel_top_left) / 2

    @property
    def panel_radius(self):
        return np.linalg.norm(self.panel_bottom_right - self.panel_top_left) / 2

    # def choose_sub_generator(self)->"ImageGenerator":
    #     keys = list(self.sub_generators.keys())
    #     probabilities = list(self.sub_generators.values())

    #     # Ensure probabilities sum to 1 (optional, if you want to validate)
    #     if not abs(sum(probabilities) - 1.0) < 1e-9:
    #         raise ValueError("Probabilities must sum to 1.")

    #     # Use random.choices to select based on weights
    #     chosen = random.choices(keys, weights=probabilities, k=1)[0]()
    #     if chosen=="chaininig":
    #         generation_config.step_into_config_scope("chaining_image_config")
    #     elif chosen=="enclosing":
    #         generation_config.step_into_config_scope("enclosing_image_config")
    #     elif chosen=="random":
    #         generation_config.step_into_config_scope("random_image_config")
    #     elif chosen=="border":
    #         generation_config.step_into_config_scope("border_image_config")
    #     elif chosen=="simple":
    #         generation_config.step_into_config_scope("simple_image_config")
    #     elif chosen=="radial":
    #         generation_config.step_into_config_scope("radial_image_config")

    #     return chosen

