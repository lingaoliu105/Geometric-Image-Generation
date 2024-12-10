

from abc import ABC, abstractmethod
from typing import List

import numpy as np

from entities.entity import VisibleShape
from generation_config import GenerationConfig



class ImageGenerator(ABC):
    
    def __init__(self) -> None:
        self.panel_top_left = np.array((GenerationConfig.left_canvas_bound,GenerationConfig.upper_canvas_bound)) # default value, allow changing from outside
        self.panel_bottom_right = np.array((GenerationConfig.right_canvas_bound,GenerationConfig.lower_canvas_bound))
        self.shapes:List[List[VisibleShape]] = [[]]
    @abstractmethod
    def generate(self):
        pass

    @property
    def panel_center(self):
        return (self.panel_bottom_right+self.panel_top_left) / 2
    
    @property
    def panel_radius(self):
        return np.linalg.norm(self.panel_bottom_right - self.panel_top_left) / 2