import json
from typing import Literal, Optional

import img_params


class GenerationConfig:
    _root_instance = None

    def __init__(self, parent: Optional['GenerationConfig'] = None):
        self.parent = parent
        # Default values that will be covered by input.json
        self.color_mode: Literal["colored", "mono"] = "colored"
        self.layout = [1,1]
        self.canvas_width: float = 20.0
        self.canvas_height: float = 20.0
        self.generate_num: int = 1
        self.generated_file_prefix: str = ""
        self.search_threshhold = 1e-5
        self.color_distribution = [1/len(list(img_params.Color))] * len(list(img_params.Color))
        self.pattern_distribution = [1/len(list(img_params.Pattern))] * len(list(img_params.Pattern))
        self.lightness_distribution = [1/len(list(img_params.Lightness))] * len(list(img_params.Lightness))
        self.background_lightness_distribution = None
        self.chaining_image_config = None
        self.radial_image_config = None
        self.random_image_config = None
        self.enclosing_image_config = None
        self.simple_image_config = None
        self.parallel_image_config = None
        self.shape_distribution = [1/len(list(img_params.Shape))] * len(list(img_params.Shape))
        self.highlight_overlap = True
        self.composition_type = {"simple":1.0}
        self.sub_composition_distribution = {}
        self.opacity = 1.0
        self.arbitrary_shape_cell_num = 10
        self.outline_distribution = [1 / len(list(img_params.Outline))] * len(
            list(img_params.Outline)
        )
        self.border_image_config = None

    def __getattr__(self, name):
        if self.parent is not None and hasattr(self.parent, name):
            return getattr(self.parent, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def create_child(self) -> 'GenerationConfig':
        return GenerationConfig(parent=self)

    @classmethod
    def get_root_instance(cls) -> 'GenerationConfig':
        if cls._root_instance is None:
            cls._root_instance = GenerationConfig()
        return cls._root_instance
    @property
    def left_canvas_bound(self):
        return -self.canvas_width/2    

    @property
    def right_canvas_bound(self):
        return self.canvas_width/2    

    @property
    def upper_canvas_bound(self):
        return self.canvas_height/2    

    @property
    def lower_canvas_bound(self):
        return -self.canvas_height/2   

    @property
    def canvas_limit(self):
        return min(self.canvas_height,self.canvas_width)

    @classmethod
    def __getattr__(cls, name):
        # 为了保持向后兼容，类属性访问会代理到根实例
        return getattr(cls.get_root_instance(), name)
