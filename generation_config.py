import json
from typing import Literal

import img_params


class GenerationConfig:
    # Those are default values. Will be covered by the input given in input.json
    color_mode: Literal["colored", "mono"] = "colored"
    layout = [1,1]
    canvas_width: float = 20.0
    canvas_height: float = 20.0
    generate_num: int = 1
    generated_file_prefix:str = ""
    search_threshhold = 1e-5 #the threshhold used when finding appropriate size / rotation using binary search
    color_distribution = [1/len(list(img_params.Color))] * len(list(img_params.Color))
    pattern_distribution = [1/len(list(img_params.Pattern))] * len(list(img_params.Pattern))
    lightness_distribution = [1/len(list(img_params.Lightness))] * len(list(img_params.Lightness))
    background_lightness_distribution = None
    chaining_image_config = None
    radial_image_config = None
    random_image_config = None
    enclosing_image_config = None
    simple_image_config = None
    shape_distribution = [1/len(list(img_params.Shape))] * len(list(img_params.Shape))
    highlight_overlap = True
    composition_type = {"simple":1.0}
    sub_composition_distribution = {}
    opacity=0.0
    arbitrary_shape_cell_num = 10
    outline_distribution = [1 / len(list(img_params.Outline))] * len(
        list(img_params.Outline)
    )
    border_image_config = None
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
