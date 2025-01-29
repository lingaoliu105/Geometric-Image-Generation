
import random
from entities.complex_shape import ComplexShape
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from generation_config import GenerationConfig
import generation_config
from image_generators.image_generator import ImageGenerator
import img_params
from shape_group import ShapeGroup
from util import get_rand_point


class SimpleImageGenerator(ImageGenerator):
    '''generate single elements like SimpleShape or LineSegment and return as ShapeGroup'''

    def __init__(self) -> None:
        super().__init__()
        self.shape_distribution = GenerationConfig.shape_distribution
    def generate(self) -> ShapeGroup:
        '''generate a single element at random position'''
        shape = random.choices(list(img_params.Shape),weights=self.shape_distribution,k=1)[0]
        if shape==img_params.Shape.linesegment:
            element = LineSegment(pt1=(GenerationConfig.left_canvas_bound,0),pt2=(GenerationConfig.right_canvas_bound,0))
        elif shape == img_params.Shape.rectangle:
            element = ComplexShape.arbitrary_rectangle()
        elif shape==img_params.Shape.triangle_rt:
            element = ComplexShape.arbitrary_right_triangle()
        else:
            element = SimpleShape(position=(0,0),shape=shape,size=GenerationConfig.canvas_width/2)
        self.shapes.add_shape(element)
        return self.shapes