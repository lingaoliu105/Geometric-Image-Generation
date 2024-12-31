from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from shape_group import ShapeGroup
from util import *


class RandomImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.element_num = GenerationConfig.random_image_config["element_num"]
        self.centralization = GenerationConfig.random_image_config["centralization"]

    def generate(self) -> ShapeGroup:
        for _ in range(self.element_num):
            position = get_rand_point() * (
                1 - generate_beta_random_with_mode(self.centralization, 2)
            )
            generator = self.choose_sub_generator()
            shape_grp = generator.generate()
            shape_grp.shift(position)
            shape_grp.scale(random.uniform(0.2, 0.4))
            shape_grp.rotate(random.choice(list(img_params.Angle)))
            self.shapes.add_group(shape_grp)

        return self.shapes
