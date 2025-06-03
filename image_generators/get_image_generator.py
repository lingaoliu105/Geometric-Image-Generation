import random
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from image_generators.simple_image_generator import SimpleImageGenerator
from image_generators.chaining_image_generator import ChainingImageGenerator
from image_generators.enclosing_image_generator import EnclosingImageGenerator
from image_generators.random_image_generator import RandomImageGenerator
from image_generators.border_image_generator import BorderImageGenerator
from image_generators.parallel_image_generator import ParallelImageGenerator
def get_image_generator(composition_type:str)->ImageGenerator:
    if composition_type == "simple":
        return SimpleImageGenerator()
    elif composition_type == "chaining":
        return ChainingImageGenerator()
    elif composition_type == "enclosing":
        return EnclosingImageGenerator()
    elif composition_type == "random":
        return RandomImageGenerator()
    elif composition_type == "border":
        return BorderImageGenerator()
    elif composition_type == "parallel":
        return ParallelImageGenerator()
    else:
        raise ValueError(f"Invalid composition type: {composition_type}")


