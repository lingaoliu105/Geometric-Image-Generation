import math
import random

import numpy as np
from responses import start
from shapely import LineString
from entities.line_segment import LineSegment
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from shape_group import ShapeGroup


class BorderImageGenerator(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.position_probabilities = GenerationConfig.border_image_config[
            "position_probabilities"
        ]
        self.element_scaling = GenerationConfig.border_image_config["element_scaling"]
        self.approach_factor = GenerationConfig.border_image_config["approach_factor"]

    def generate(self):
        canvas_corner_points = np.array(
            [
                (
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
                ),
            ]
        )
        canvas_boundary_geometry = LineString(canvas_corner_points)
        shrinked_boundary = LineString(canvas_corner_points * self.approach_factor)
        for entry, probability in enumerate(self.position_probabilities[:-1]):
            move_direction_angle = 135 + 45 * entry
            move_direction_vector = np.array(
                (
                    math.cos(math.radians(move_direction_angle)),
                    math.sin(math.radians(move_direction_angle)),
                )
            )
            if random.random() <= probability:
                sub_image = self.choose_sub_generator().generate()
                if sub_image.size() == 1 and isinstance(sub_image[0][0], LineSegment):

                    large_distance = 1000
                    end_point = (
                        np.array((0, 0)) + move_direction_vector * large_distance
                    )
                    ray = LineString([np.array((0, 0)), end_point])

                    # Find the intersection between the ray and the boundary geometry
                    intersection = ray.intersection(canvas_boundary_geometry)

                    pt2 = np.array(intersection.coords[0])

                    sub_image = ShapeGroup(
                        [[LineSegment(pt1=np.array((0, 0)), pt2=pt2)]]
                    )
                else:
                    sub_image.scale(self.element_scaling)
                    while not sub_image.geometry(0).intersects(shrinked_boundary):
                        sub_image.shift(move_direction_vector * 0.1)
                self.shapes.add_group(sub_image)

        if random.random() < self.position_probabilities[-1]:
            sub_image = self.choose_sub_generator().generate()
            sub_image.scale(self.element_scaling)
            self.shapes.add_group(sub_image)

        return self.shapes
