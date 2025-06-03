
import random
from entities.complex_shape import ComplexShape
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from generation_config import GenerationConfig
import generation_config
from image_generators.image_generator import ImageGenerator
import img_params
from input_configs import SimpleImageConfig
from shape_group import ShapeGroup
from util import get_rand_point


class SimpleImageGenerator(ImageGenerator):
    '''
    Generate single elements like SimpleShape or LineSegment and return as ShapeGroup
    No further sub elements
    '''

    def __init__(self) -> None:
        super().__init__()
        self.shape_distribution = GenerationConfig.shape_distribution
        self.config:SimpleImageConfig = GenerationConfig.simple_image_config

    def generate(self) -> ShapeGroup:
        '''generate a single element with deterministic configuration'''
        shape = random.choices(list(img_params.Shape), weights=self.shape_distribution, k=1)[0]
        
        if shape == img_params.Shape.linesegment:
            element = LineSegment(pt1=(-GenerationConfig.canvas_limit/2,0), pt2=(GenerationConfig.canvas_limit/2,0))
        elif shape == img_params.Shape.rectangle:
            aspect_ratio = random.uniform(self.config.aspect_ratio.min, self.config.aspect_ratio.max)
            element = ComplexShape.arbitrary_rectangle(aspect_ratio=aspect_ratio)
        elif shape == img_params.Shape.triangle_rt:
            aspect_ratio = random.uniform(self.config.aspect_ratio.min, self.config.aspect_ratio.max)
            element = ComplexShape.arbitrary_right_triangle(aspect_ratio=aspect_ratio)
        elif shape == img_params.Shape.arbitrary:
            element = ComplexShape.arbitrary_polygon()
        else:
            element = SimpleShape(position=(0,0),shape=shape,size=min(GenerationConfig.canvas_width,GenerationConfig.canvas_height)/2,rotation=img_params.Angle.deg0)
        self.shapes.add_shape(element)
        return self.shapes