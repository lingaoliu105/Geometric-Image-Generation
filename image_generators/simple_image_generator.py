
import random
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from generation_config import GenerationConfig
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
            print('chosen line segment')
            element = LineSegment()
        else:
            element = SimpleShape(position=get_rand_point(),shape=shape)
        self.shapes.add_shape(element)
        return self.shapes