from typing import Literal


class GenerationConfig:
    color_mode: Literal["colored", "mono"] = "colored"
    canvas_width: float = 20.0
    canvas_height: float = 20.0
    generate_num: int = 1

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
