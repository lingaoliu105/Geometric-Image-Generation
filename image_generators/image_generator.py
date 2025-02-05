from abc import ABC, abstractmethod
import random
import re
from typing import Dict, List

import numpy as np

from generation_config import GenerationConfig

from shape_group import ShapeGroup


class ImageGenerator(ABC):

    def __init__(self) -> None:
        self.shapes:ShapeGroup = ShapeGroup([[]])
        from image_generators.simple_image_generator import SimpleImageGenerator
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
        self.sub_generators = {}
        self.__set_sub_generators()
    @abstractmethod
    def generate(self)->ShapeGroup:
        pass

    @property
    def panel_center(self):
        return (self.panel_bottom_right+self.panel_top_left) / 2

    @property
    def panel_radius(self):
        return np.linalg.norm(self.panel_bottom_right - self.panel_top_left) / 2

    def choose_sub_generator(self)->"ImageGenerator":
        keys = list(self.sub_generators.keys())
        probabilities = list(self.sub_generators.values())

        # Ensure probabilities sum to 1 (optional, if you want to validate)
        if not abs(sum(probabilities) - 1.0) < 1e-9:
            raise ValueError("Probabilities must sum to 1.")

        # Use random.choices to select based on weights
        return random.choices(keys, weights=probabilities, k=1)[0]()


    def __set_sub_generators(self):
        '''only be called when the generator is top-level generator'''
        # self.sub_generators.clear() # clear default value

        for generator_type in self.distribution_dict: 
            if generator_type == "chain":
                from image_generators.chaining_image_generator import ChainingImageGenerator
                generator = ChainingImageGenerator
            elif generator_type == "enclosing":
                from image_generators.enclosing_image_generator import EnclosingImageGenerator
                generator = EnclosingImageGenerator
            elif generator_type=="random":
                from image_generators.random_image_generator import RandomImageGenerator
                generator = RandomImageGenerator
            elif generator_type=="border":
                from image_generators.border_image_generator import BorderImageGenerator
                generator = BorderImageGenerator
            else: # simple generator as default
                from image_generators.simple_image_generator import SimpleImageGenerator
                generator = SimpleImageGenerator
                
            self.sub_generators[generator] = self.distribution_dict[generator_type]
