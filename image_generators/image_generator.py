from abc import ABC, abstractmethod
import random
from typing import Dict, List

import numpy as np

from generation_config import GenerationConfig

from shape_group import ShapeGroup


class ImageGenerator(ABC):

    def __init__(self) -> None:
        self.shapes:ShapeGroup = ShapeGroup([[]])
        from image_generators.simple_image_generator import SimpleImageGenerator
        self.sub_generators:Dict[ImageGenerator,float] = {SimpleImageGenerator:1.0}
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


    def set_sub_generators(self):
        '''only be called when the generator is top-level generator'''
        self.sub_generators.clear() # clear default value
        distribution_dict = GenerationConfig.sub_composition_distribution

        for generator_type in distribution_dict: 
            if generator_type == "chain":
                from image_generators.chaining_image_generator import ChainingImageGenerator
                generator = ChainingImageGenerator
            elif generator_type == "enclosing":
                from image_generators.enclosing_image_generator import EnclosingImageGenerator
                generator = EnclosingImageGenerator
            elif generator_type=="random":
                from image_generators.random_image_generator import RandomImageGenerator
                generator = RandomImageGenerator
            else: # simple generator as default
                from image_generators.simple_image_generator import SimpleImageGenerator
                generator = SimpleImageGenerator
                
            self.sub_generators[generator] = distribution_dict[generator_type]
