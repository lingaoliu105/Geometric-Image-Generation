import copy
import math
import random
from typing import List

import numpy as np
from shapely import LineString, Polygon, MultiPolygon
from entities.complex_shape import ComplexShape
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
        self.shade_probability = GenerationConfig.border_image_config[
            "shade_probability"
        ]
        self.spokes: List[LineSegment] = []
        self.shaded_areas: List[ComplexShape] = []

    def generate(self):
        self.canvas_corner_points = np.array(
            [
                (
                    GenerationConfig.right_canvas_bound,
                    GenerationConfig.upper_canvas_bound,
                ),
                (
                    GenerationConfig.left_canvas_bound,
                    GenerationConfig.upper_canvas_bound,
                ),
                (
                    GenerationConfig.left_canvas_bound,
                    GenerationConfig.lower_canvas_bound,
                ),
                (
                    GenerationConfig.right_canvas_bound,
                    GenerationConfig.lower_canvas_bound,
                ),
                (
                    GenerationConfig.right_canvas_bound,
                    GenerationConfig.upper_canvas_bound,
                ),
            ]
        )
        canvas_boundary_geometry = LineString(self.canvas_corner_points)
        shrinked_boundary = LineString(self.canvas_corner_points * self.approach_factor)
        for entry, probability in enumerate(self.position_probabilities[:-1]):
            move_direction_angle = 45 * entry  # starting from 0 degree counterclockwise
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
                    spoke = LineSegment(pt1=np.array((0, 0)), pt2=pt2)
                    spoke.angle = move_direction_angle
                    sub_image = ShapeGroup([[spoke]])
                    self.spokes.append(spoke)
                else:
                    step_length = 0.05
                    sub_image.scale(self.element_scaling)
                    sub_image.rotate(random.choice(list(range(0, 361, 90))))
                    xoff = 0
                    yoff = 0
                    if not math.isclose(move_direction_vector[0], 0.0, abs_tol=1e-9):
                        cpy = copy.deepcopy(sub_image)
                        while not cpy.geometry(0).intersects(shrinked_boundary):
                            cpy.shift(
                                np.array([move_direction_vector[0], 0]) * step_length
                            )
                            xoff += step_length
                    if not math.isclose(move_direction_vector[1], 0.0, abs_tol=1e-9):
                        cpy = copy.deepcopy(sub_image)
                        while not cpy.geometry(0).intersects(shrinked_boundary):
                            cpy.shift(
                                np.array([0, move_direction_vector[1]]) * step_length
                            )
                            yoff += step_length
                    sub_image.shift(
                        [
                            xoff * move_direction_vector[0],
                            yoff * move_direction_vector[1],
                        ]
                    )
                self.shapes.add_group(sub_image)

        if random.random() < self.position_probabilities[-1]:
            sub_image = self.choose_sub_generator().generate()
            if isinstance(sub_image.geometry(0), Polygon) or isinstance(
                sub_image.geometry(0), MultiPolygon
            ):
                sub_image.scale(self.element_scaling)
                self.shapes.add_group(sub_image)

        self.shade_regions()
        return self.shapes

    def shade_regions(self):
        if len(self.spokes) <= 1:
            return

        corner_angles = [45 + i * 90 for i in range(4)]
        corner_angles_small = []
        for i in range(-1, len(self.spokes) - 1):
            if random.random() < self.shade_probability:
                start_edge = self.spokes[i]
                start_angle = start_edge.angle
                end_edge = self.spokes[i + 1]
                end_angle = end_edge.angle
                vertices = []
                start_endpts = [start_edge.endpt_left, start_edge.endpt_right]
                start_endpts.sort(key=lambda coord: coord[0] ** 2 + coord[1] ** 2)
                start_pt = start_endpts[1]
                end_endpts = [end_edge.endpt_left, end_edge.endpt_right]
                end_endpts.sort(key=lambda coord: coord[0] ** 2 + coord[1] ** 2)
                end_pt = end_endpts[1]
                for corner_index in range(4):
                    print(start_angle, corner_angles[corner_index], end_angle)
                    if (
                        start_angle >= end_angle
                        and corner_angles[corner_index] > start_angle
                        and corner_angles[corner_index] < end_angle
                    ) or (
                        start_angle > end_angle
                        and corner_angles[corner_index] > start_angle
                        or corner_angles[corner_index] < end_angle
                    ):
                        vertices.append(self.canvas_corner_points[corner_index])
                        vertices.sort(key=lambda vertex:math.atan2(vertex[0],vertex[1]))
                        
                                        
                final_vertices = [(0, 0)] + [start_pt] + vertices + [end_pt] + [(0,0)]
                self.shaded_areas.append(ComplexShape(geometry=Polygon(final_vertices)))

        self.shapes.lift_up_layer()
        for area in self.shaded_areas:
            self.shapes.add_shape(area)
