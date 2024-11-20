from functools import reduce
from math import ceil

from shapely import unary_union
from entities.complex_shape import ComplexShape
from entities.simple_shape import SimpleShape
from image_generators.image_generator import ImageGenerator
from panel import Panel
from util import *


class RandomImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.element_num = ceil(generate_beta_random_with_mode(0.3, 2) * 19) + 1
        self.union_geometries = [] #index is layer of display
        
        

    def generate(self):
        for _ in range (self.element_num):
            shape = SimpleShape(position=get_rand_point())
            self.shapes[0].append(shape)
            new_overlaps = [shape]
            for layer,union_geometry in enumerate(self.union_geometries):
                if shape.base_geometry.overlaps(union_geometry):
                    if len(self.shapes)<=layer+1:
                        self.shapes.append([])
                    new_overlaps = ComplexShape.from_overlapping_geometries(shape.base_geometry,union_geometry)
                    self.shapes[layer+1]+=new_overlaps
                    new_overlaps+=(new_overlaps)
                    
            for layer,overlap in enumerate(new_overlaps):
                if layer > len(self.union_geometries)-1:
                    self.union_geometries.append(overlap.base_geometry)
                self.union_geometries[layer] = unary_union([self.union_geometries[layer],overlap.base_geometry])
        return Panel(top_left=self.panel_top_left,bottom_right=self.panel_bottom_right,shapes = reduce(lambda x,y:x+y,self.shapes),joints=[])
