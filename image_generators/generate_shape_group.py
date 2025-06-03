import random

from generation_config import GenerationConfig
from image_generators import get_image_generator
from shape_group import ShapeGroup

def generate_shape_group():
    composition_type = random.choices(
        list(GenerationConfig.composition_type.keys()),
        list(GenerationConfig.composition_type.values()),
    )[0]
    generator = get_image_generator(composition_type)
    elements: ShapeGroup = generator.generate()
    return elements
