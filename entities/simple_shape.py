import math
import random
from typing import Optional

import numpy as np
from shapely.geometry import Point, Polygon

import common_types
import img_params
from entities.closed_shape import ClosedShape
from entities.visible_shape import VisibleShape
from img_params import *
from tikz_converters import SimpleShapeConverter


class SimpleShape(ClosedShape):

    dataset_annotation_categories = [
        "pattern",
        "color",
        "lightness",
        "pattern_color",
        "pattern_lightness",
        "outline",
        "outline_color",
        "outline_thickness",
        "outline_lightness",
    ]  # attributes that can be directly interpreted as categories in dataset annotations

    serialized_fields = [
        "uid",
        "shape",
        "size",
        "position",
        "rotation",
        "base_geometry",
    ] + dataset_annotation_categories

    touching_tolerance = 1e-11

    def __init__(
        self,
        position: np.ndarray,
        rotation: Optional[img_params.Angle] = None,
        size: Optional[float] = None,
        shape: Optional[img_params.Shape] = None,
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
        pattern: Optional[img_params.Pattern] = None,
        outline=None,
        outline_lightness=None,
        pattern_color=None,
        pattern_lightness=None,
        outline_color=None,
        outline_thickness=None,
        excluded_shapes_set: set = {},
    ) -> None:
        super().__init__(
            tikz_converter=SimpleShapeConverter(),
            color=color,
            lightness=lightness,
            pattern=pattern,
            outline=outline,
            outline_lightness=outline_lightness,
            pattern_color=pattern_color,
            pattern_lightness=pattern_lightness,
            outline_color=outline_color,
            outline_thickness=outline_thickness,
        )
        self.position = position
        self.rotation = rotation if rotation is not None else random.choice(list(img_params.Angle))
        self.shape = (
            shape
            if shape is not None
            else random.choice(
                [
                    x
                    for x in list(img_params.Shape)[1:6]
                    if x not in excluded_shapes_set
                    and x != img_params.Shape.linesegment
                ]
            )
        )
        # self.type = filter(list(img_params.Type))
        self.size = (
            size
            if size is not None
            else (random.random() + 0.25) * 2
        )
   
        self.is_expanded = False
        self.compute_base_geometry()

    def compute_base_geometry(self):
        rot_rad = math.radians(self.rotation.value)
        rot_sin = math.sin(rot_rad)
        rot_cos = math.cos(rot_rad)
        rot_polar = np.array((rot_cos, rot_sin))
        rot_cart = self.size * rot_polar

        # TODO: complete other shapes. remember to add last -- first
        if self.shape == Shape.circle:
            self._base_geometry = Point(self.position).buffer(self.size)
        else:
            if self.shape == Shape.triangle:
                angle_list = [-30, 90, 210]
            elif self.shape == Shape.square:
                angle_list = [-45, 45, 135, 225]
            elif self.shape == Shape.pentagon:
                angle_list = [-54 + 72 * x for x in range(5)]
            elif self.shape == Shape.hexagon:
                angle_list = [60 * x for x in range(6)]
            else:
                raise ValueError(f"illegal shape: {self.shape}")

            vertices = [None] * (len(angle_list))
            index = 0
            for angle in angle_list:
                rot_rad = math.radians(angle + self.rotation.value)
                rot_sin = math.sin(rot_rad)
                rot_cos = math.cos(rot_rad)
                rot_polar = np.array((rot_cos, rot_sin))
                rot_cart = self.size * rot_polar
                vertices[index] = self.position + rot_cart
                index += 1
            self._base_geometry = Polygon(vertices)

    def get_vertices(self) -> list:
        return self._base_geometry.exterior.coords

    def get_attach_point(self) -> np.ndarray:
        if self.shape == Shape.circle:
            rand_rad = random.random() * 2 * math.pi
            return self.position + self.size * np.array(
                [math.cos(rand_rad), math.sin(rand_rad)]
            )
        fraction = (
            random.choice(list(TouchingPosition)).value * random.randint(1, 5) % 1
        )
        vertices = self.get_vertices()
        edge_index = random.randint(
            0, len(vertices) - 2
        )  # the edge is vert[index] -- vert[index+1]
        return vertices[edge_index] + fraction * (
            vertices[edge_index + 1] - vertices[edge_index]
        )

    def check_overlap(self, other: "SimpleShape") -> bool:
        return self._base_geometry.overlaps(other._base_geometry)

    def set_size(self, new_size: float):
        self.size = new_size
        self.compute_base_geometry()
        
    def scale(self,ratio,origin="center"):
        super().scale(ratio,origin)
        self.position = self._base_geometry.centroid.coords[0]
        new_size = self.size * ratio
        self.size = new_size

    # def search_touching_size(self, other: VisibleShape):
    #     """with a initial size that guarantees to overlap, search the appropriate size that touches the other shape (with tolerance defined in the class), and set the own size to it

    #     Args:
    #         other (SimpleShape): the other size you want to touch
    #     """
    #     # TODO: optimize performance
    #     upper = self.size
    #     lower = 0.1
    #     other_shape = other.base_geometry
    #     while (
    #         not other_shape.touches(self._base_geometry)
    #         and (upper - lower) > self.touching_tolerance
    #     ):
    #         mid = (upper + lower) / 2.0
    #         self.set_size(mid)
    #         if (
    #             self._base_geometry.overlaps(other_shape)
    #             or self._base_geometry.intersects(other_shape)
    #             or self._base_geometry.contains(other_shape)
    #         ):
    #             upper = mid
    #         else:
    #             lower = mid

    # def search_size_by_interval(self, other: "VisibleShape", interval: float):
    #     padded_other = other.expand_fixed(interval)
    #     self.search_touching_size(padded_other)

    def shift(self, offset: common_types.Coordinate):
        offset = np.array(offset)
        self.position += offset
        super().shift(offset=offset)

    def expand_fixed(self, length):
        cpy = self.copy
        cpy.set_size(max(self.size + length,0.1))
        return cpy

    def expand(self, ratio):
        self.set_size(self.size * ratio)
        return self

    @property
    def center(self):
        return self.position

    def overlaps(self, other: VisibleShape):
        return super().overlaps(other)

    def rotate(self,angle,origin="center"):
        super().rotate(angle,origin)
        # TODO: make better representation of rotation
        def get_relative_rotation(polygon: Polygon) -> float:
            """
            Calculate the relative rotation of a polygon compared to its horizontal placement.
            
            :param polygon: A Shapely Polygon object.
            :return: Rotation angle in degrees, counterclockwise relative to the horizontal axis.
            """
            # Get the minimum rotated rectangle
            rotated_rect = polygon.minimum_rotated_rectangle
            
            # Extract the rectangle's coordinates (it will be a closed loop)
            rect_coords = list(rotated_rect.exterior.coords)[:4]  # Get the 4 corners
            
            # Compute the vector along one of the longer sides
            vec1 = (rect_coords[1][0] - rect_coords[0][0], rect_coords[1][1] - rect_coords[0][1])
            vec2 = (rect_coords[2][0] - rect_coords[1][0], rect_coords[2][1] - rect_coords[1][1])
            
            # Choose the longer vector as the main axis
            if (vec1[0]**2 + vec1[1]**2) >= (vec2[0]**2 + vec2[1]**2):
                main_axis = vec1
            else:
                main_axis = vec2
            
            # Calculate the angle with the horizontal axis
            angle = math.degrees(math.atan2(main_axis[1], main_axis[0]))
            
            # Normalize angle to [0, 180) or [0, 360) as needed
            angle = angle % 180  # Keep in [0, 180) for bidirectional comparison
            return angle
        actual_rotation_angle = get_relative_rotation(self._base_geometry)
        self.rotation = min(list(img_params.Angle),key=lambda x:abs(actual_rotation_angle - x.value))
        self.position = self._base_geometry.centroid.coords[0]
        