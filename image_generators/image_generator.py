

from abc import ABC, abstractmethod
from typing import List

from entities.entity import VisibleShape
from generation_config import GenerationConfig



class ImageGenerator(ABC):
    
    def __init__(self) -> None:
        self.panel_top_left = (GenerationConfig.left_canvas_bound,GenerationConfig.upper_canvas_bound)
        self.panel_bottom_right = (GenerationConfig.right_canvas_bound,GenerationConfig.lower_canvas_bound)
        self.shapes:List[List[VisibleShape]] = [[]]
    @abstractmethod
    def generate(self):
        pass