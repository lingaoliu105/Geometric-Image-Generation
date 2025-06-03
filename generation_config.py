import json
from typing import Literal, Union

import img_params
from input_configs import (
    BaseConfig,
    ElementConfig,
    PanelConfig,
    ChainingImageConfig,
    EnclosingImageConfig,
    RadialImageConfig,
    RandomImageConfig,
    SimpleImageConfig
)
from dataclasses import fields, dataclass


class DynamicClassAttributesMeta(type):
    def __getattr__(cls, name):
        searched_config = cls.current_config
        print(f"searching {name} in {searched_config.__class__.__name__}")
        while searched_config is not None:
            try:
                attr = getattr(searched_config, name)
                if attr is not None:
                    return attr
                else:
                    raise AttributeError(f"{name} is None in {searched_config.__class__.__name__}")
            except AttributeError:
                print(f"did not find {name} in {searched_config.__class__.__name__}")
                try:
                    searched_config = searched_config.parent
                except AttributeError:
                    raise AttributeError(f"did not find parent config for {searched_config.__class__.__name__}, search chain ended")
                except:
                    raise AttributeError(f"{name} not found in any config")


@dataclass
class GenerationConfig(metaclass=DynamicClassAttributesMeta):
    # pointer to the config object that is currently being used
    current_config: Union[BaseConfig, PanelConfig, ElementConfig] = None
    
    # Those are default values. Will be covered by the input given in input.json
    # color_mode: Literal["colored", "mono"] = "colored"
    # layout = [1,1]
    # canvas_width: float = 20.0
    # canvas_height: float = 20.0
    # generate_num: int = 1
    # generated_file_prefix:str = ""
    # search_threshhold = 1e-5 #the threshhold used when finding appropriate size / rotation using binary search
    # color_distribution = [1/len(list(img_params.Color))] * len(list(img_params.Color))
    # pattern_distribution = [1/len(list(img_params.Pattern))] * len(list(img_params.Pattern))
    # lightness_distribution = [1/len(list(img_params.Lightness))] * len(list(img_params.Lightness))
    # background_lightness_distribution = None
    # chaining_image_config:ChainingImageConfig = None
    # radial_image_config:RadialImageConfig = None
    # random_image_config:RandomImageConfig = None
    # enclosing_image_config:EnclosingImageConfig = None
    # simple_image_config:SimpleImageConfig = None
    # shape_distribution = [1/len(list(img_params.Shape))] * len(list(img_params.Shape))
    # highlight_overlap = True
    # composition_type = {"simple":1.0}
    # sub_composition_distribution = {}
    # opacity=0.0
    # arbitrary_shape_cell_num = 10
    # outline_distribution = [1 / len(list(img_params.Outline))] * len(
    #     list(img_params.Outline)
    # )
    # border_image_config = None
    @classmethod
    @property
    def left_canvas_bound(self):
        return -self.canvas_width/2    
    @classmethod
    @property
    def right_canvas_bound(self):
        return self.canvas_width/2    
    @classmethod
    @property
    def upper_canvas_bound(self):
        return self.canvas_height/2    
    @classmethod
    @property
    def lower_canvas_bound(self):
        return -self.canvas_height/2   
    @classmethod
    @property
    def canvas_limit(self):
        return min(self.canvas_height,self.canvas_width)


def step_into_config_scope_decorator(func):
    def wrapper(self, *args, **kwargs):
        generator_class = self.__class__
        print(f"step into {generator_class.__name__}")
        lookup_dict = {
            "ChainingImageGenerator": "chaining_image_config",
            "EnclosingImageGenerator": "enclosing_image_config",
            "RadialImageGenerator": "radial_image_config",
            "RandomImageGenerator": "random_image_config",
            "SimpleImageGenerator": "simple_image_config"
        }
        if len(GenerationConfig.current_config.child_configs) == 0:
            key = lookup_dict[generator_class.__name__]
            if key != "simple_image_config":
                GenerationConfig.current_config.child_configs = getattr(GenerationConfig.current_config, key).sub_elements
                GenerationConfig.current_config.iterate_next_child_to_access()
        if GenerationConfig.current_config.next_child_to_access is None:
            raise ValueError("No config object to access")
        else:
            next_child = GenerationConfig.current_config.next_child_to_access
            GenerationConfig.current_config = next_child
            return func(self, *args, **kwargs)
    return wrapper

def step_into_config_scope(img_config_name):
    if len(GenerationConfig.current_config.child_configs) == 0:

        if img_config_name != "simple_image_config":
            GenerationConfig.current_config.child_configs = getattr(GenerationConfig.current_config, img_config_name).sub_elements
            GenerationConfig.current_config.iterate_next_child_to_access()
    if GenerationConfig.current_config.next_child_to_access is None:
        raise ValueError("No config object to access")
    else:
        next_child = GenerationConfig.current_config.next_child_to_access
        GenerationConfig.current_config = next_child
def step_out_config_scope(func):
    def wrapper(self, *args, **kwargs):
        GenerationConfig.current_config = GenerationConfig.current_config.parent
        return func(self, *args, **kwargs)
    return wrapper
