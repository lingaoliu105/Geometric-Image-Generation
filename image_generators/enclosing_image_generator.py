
import random

import numpy as np
from entities.simple_shape import SimpleShape
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
import img_params
from shape_group import ShapeGroup


class EnclosingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.enclose_level = GenerationConfig.enclosing_image_config["enclose_level"]
        
        
    def generate(self)->ShapeGroup:
        print("enclosing:",self.sub_generators)
        self.canvas_radius_limit = min(GenerationConfig.canvas_height/2,GenerationConfig.canvas_width/2)
        self.generate_composite_image_nested(self.canvas_radius_limit,self.enclose_level)
        return self.shapes
        
        
    def generate_composite_image_nested(
        self,outer_radius, recur_depth
    ):
        """generate a nested image, centered at 0,0, and within a square area of outer_size * outer_size
        """
        print("hello:",recur_depth)
        if recur_depth <= 1:
            core_generator = self.choose_sub_generator() # sub generator is only used for core image
            core_shape_group = core_generator.generate() 
            
            shrink_ratio = outer_radius / self.canvas_radius_limit
            core_shape_group.scale(shrink_ratio,origin=(0,0))  
            self.shapes.add_group(core_shape_group)
        else:
            outer_shape = SimpleShape(np.array([0.0, 0.0]), rotation = random.choice(list(img_params.Angle)), size=outer_radius)
            self.shapes.add_shape(outer_shape)
            if outer_shape.shape == img_params.Shape.triangle:
                shrink_ratio = 0.4
            else:
                shrink_ratio = 0.6
            self.generate_composite_image_nested(outer_radius=outer_radius * shrink_ratio,recur_depth=recur_depth-1)
