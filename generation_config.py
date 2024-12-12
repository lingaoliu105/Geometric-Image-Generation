import json
from typing import Literal

import img_params


class GenerationConfig:
    color_mode: Literal["colored", "mono"] = "colored"
    canvas_width: float = 20.0
    canvas_height: float = 20.0
    generate_num: int = 1
    generated_file_prefix:str = ""
    search_threshhold = 1e-5 #the threshhold used when finding appropriate size / rotation using binary search
    color_distribution = [1/len(list(img_params.Color))] * len(list(img_params.Color))
    chaining_image_config = None
    radial_image_config = None
    random_image_config = None

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
        return -self.canvas_width/2   

