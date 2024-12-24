from functools import reduce
from math import ceil

from shapely import unary_union
from entities.complex_shape import ComplexShape
from entities.simple_shape import SimpleShape
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from panel import Panel
from shape_group import ShapeGroup
from util import *


class RandomImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.element_num = GenerationConfig.random_image_config["element_num"]
        self.centralization = GenerationConfig.random_image_config["centralization"]
        

    def generate(self)->ShapeGroup:
        for _ in range (self.element_num):
            generator = self.choose_sub_generator()
            shape_grp = generator.generate()
            self.shapes.add_group(shape_grp)
        return ShapeGroup(shapes = reduce(lambda x,y:x+y,self.shapes))
