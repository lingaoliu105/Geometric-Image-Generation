import math
import random

import numpy as np
from shapely import LineString
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator


class BorderImageGenerator(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.position_probabilities = GenerationConfig.border_image_config['position_probabilities']

    def generate(self):
        for entry, probability in enumerate(self.position_probabilities):
            move_direction_angle = 135 + 45 * entry
            move_direction_vector = np.array(
                (
                    math.cos(math.radians(move_direction_angle)),
                    math.sin(math.radians(move_direction_angle)),
                )
            )
            canvas_boundary_geometry = LineString(
                [(
                    GenerationConfig.left_canvas_bound,
                    GenerationConfig.upper_canvas_bound,
                ),
                (
                    GenerationConfig.right_canvas_bound,
                    GenerationConfig.upper_canvas_bound,
                ),
                (
                    GenerationConfig.right_canvas_bound,
                    GenerationConfig.lower_canvas_bound,
                ),
                (
                    GenerationConfig.left_canvas_bound,
                    GenerationConfig.lower_canvas_bound,
                ),
                (
                    GenerationConfig.left_canvas_bound,
                    GenerationConfig.upper_canvas_bound,
                )]
            )
            if random.random() <= probability:
                sub_image = self.choose_sub_generator().generate()
                sub_image.scale(0.3)
                while not sub_image.geometry(0).intersects(canvas_boundary_geometry):
                    sub_image.shift(move_direction_vector * 0.1)
                self.shapes.add_group(sub_image)
                    
        return self.shapes
