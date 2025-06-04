import copy
import random
from typing import Optional, Union

import numpy as np
from shapely import LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry

import generation_config
import img_params
import util
from common_types import *
from entities.visible_shape import OpenShape, VisibleShape
from tikz_converters import LineSegmentConverter
from util import (almost_equal, generate_random_points_around_point,
                  get_line_rotation, get_point_distance, get_rand_point)


class LineSegment(OpenShape):
    dataset_annotation_categories = [
        "position",
        "shape",
        "color",
        "lightness",
    ]  # attributes that can be directly interpreted as categories in dataset annotations

    serialized_fields = [
        "uid",
        "base_geometry",
    ] + dataset_annotation_categories

    endpt_comp_key_lr = lambda p: (p[0], -p[1])
    endpt_comp_key_ud = lambda p: (p[1], -p[0])

    def __init__(
        self,
        pt1: Optional[Union[np.ndarray, tuple, list]] = None,
        pt2: Optional[Union[np.ndarray, tuple, list]] = None,
        color = None
    ) -> None:
        super().__init__(tikz_converter=LineSegmentConverter(),color=color)
        self.shape = img_params.Shape.linesegment
        if pt1 is None and pt2 is None:
            # if neither points is specified, choose both points randomly
            self._base_geometry = LineString([get_rand_point() for _ in range(2)])
        elif pt1 is None:
            self._base_geometry = LineString([pt2, get_rand_point()])
        elif pt2 is None:
            self._base_geometry = LineString([pt1, get_rand_point()])
        else:
            self._base_geometry = LineString([pt1, pt2])

        self.line_pattern = util.choose_item_by_distribution(
            img_params.Outline, generation_config.GenerationConfig.outline_distribution
        )
        self.is_expanded = False

    @property
    def base_geometry(self):
        if self.is_expanded:
            return self._base_geometry_expanded
        else:
            return self._base_geometry

    @staticmethod
    def within_distance(point: Coordinate, distance: float):
        pt1, pt2 = generate_random_points_around_point(center=point, distance=distance)
        ls = LineSegment(pt1, pt2)
        if ls.length <= 0.5:
            ls.scale(2)
        return ls

    @property
    def endpt_left(self) -> np.ndarray:
        endpt_coords = self._base_geometry.coords
        assert len(endpt_coords) == 2
        pt1, pt2 = np.array(endpt_coords)
        return min(pt1, pt2, key=LineSegment.endpt_comp_key_lr)

    @property
    def endpt_right(self) -> np.ndarray:
        endpt_coords = self._base_geometry.coords
        assert len(endpt_coords) == 2
        pt1, pt2 = endpt_coords
        return max(pt1, pt2, key=LineSegment.endpt_comp_key_lr)

    @property
    def endpt_up(self) -> np.ndarray:
        endpt_coords = self._base_geometry.coords
        assert len(endpt_coords) == 2
        pt1, pt2 = endpt_coords
        return max(pt1, pt2, key=LineSegment.endpt_comp_key_ud)

    @property
    def endpt_down(self) -> np.ndarray:
        endpt_coords = self._base_geometry.coords
        assert len(endpt_coords) == 2
        pt1, pt2 = endpt_coords
        return min(pt1, pt2, key=LineSegment.endpt_comp_key_ud)

    @property
    def center(self) -> np.ndarray:
        pt1, pt2 = map(np.array, [self.endpt_left, self.endpt_right])
        return np.array((pt1 + pt2) / 2)

    @property
    def midpoint(self):
        return self.center

    @property
    def position(self):
        return self.center

    @property
    def length(self):
        return get_point_distance(self.endpt_left, self.endpt_right)

    @property
    def radius(self):
        return self.length / 2

    @property
    def rotation(self):
        return get_line_rotation(self.endpt_left, self.endpt_right)

    def set_endpoints(self, pt1: Coordinate, pt2: Coordinate):
        self._base_geometry = LineString([pt1, pt2])

    def find_fraction_point(self, fraction: float):
        return self.endpt_left + (self.endpt_right - self.endpt_left) * fraction

    def rotated_copy(self, pivot, angle):
        cpy = copy.deepcopy(self)
        cpy.rotate(pivot, angle)
        return cpy

    def overlaps(self, other: VisibleShape):
        return self._base_geometry.intersects(other.base_geometry)

    def expand_fixed(self, length):
        if almost_equal(length, 0.0):
            pass
        elif length > 0:
            if self.is_expanded:  # reset if already expanded before
                self._base_geometry_expanded = self._base_geometry
            self._base_geometry_expanded = self._base_geometry.buffer(length)
            self.is_expanded = True
        elif length < 0:
            self.scale(1 - 2 * abs(length) / self.length)
        return self

    def scale_with_pivot(self, ratio, pivot: Coordinate):
        assert self._base_geometry.buffer(0.01).contains(Point(pivot))
        pivot = np.array(pivot)
        offset1 = self.endpt_left - pivot
        offset2 = self.endpt_right - pivot
        self._base_geometry = LineString(
            [pivot + offset1 * ratio, pivot + offset2 * ratio]
        )

    def expand(self, ratio):
        self.scale(ratio=ratio)

    @staticmethod
    def connect(object1: BaseGeometry, object2: BaseGeometry) -> "LineSegment":
        def choose_endpoint_around_shape(shape: Polygon, ref_point: Coordinate):
            def sample_geometry_boundary(geometry, num_points=30) -> Coordinate:
                if isinstance(geometry, Polygon):
                    # 获取多边形的外环
                    exterior_coords = geometry.exterior.coords
                    if len(exterior_coords) >= num_points:  # most likely a circle
                        return exterior_coords
                    geometry = LineString(exterior_coords)

                # 根据周长进行等距采样
                sampled_points = []
                for i in np.linspace(0, geometry.length, num_points):
                    sampled_points.append(geometry.interpolate(i).coords[0])
                return sampled_points

            assert not isinstance(shape, LineString)
            # pick a point on the expanded shape, which faces the next endpoint
            bound_points: list = sample_geometry_boundary(shape)
            filtered_bound_points = list(
                filter(
                    lambda point: not LineString([point, ref_point]).intersects(shape)
                    or LineString([point, ref_point]).touches(shape),
                    bound_points,
                )
            )
            if (
                len(filtered_bound_points) == 0
            ):  # don't know why no point passed the filter. if so, simply choose the point directly facing the next endpoint
                return (
                    LineString([ref_point, shape.centroid.coords[0]])
                    .intersection(shape.base_geometry.buffer(0.01))
                    .coords[0]
                )
            return random.choice(filtered_bound_points)

        if isinstance(object1, Polygon) and isinstance(object2, Polygon):
            pt1 = choose_endpoint_around_shape(object1, object2.centroid.coords[0])
            pt2 = choose_endpoint_around_shape(object2, pt1)
        elif isinstance(object2, Polygon):
            pt1 = object1.coords[0]
            pt2 = choose_endpoint_around_shape(object2, pt1)
        elif isinstance(object1, Polygon):
            pt1 = object2.coords[0]
            pt2 = choose_endpoint_around_shape(object1, pt1)
        elif isinstance(object1, Point) and isinstance(object2, Point):
            pt1, pt2 = object1.coords[0], object2.coords[0]
        else:
            raise TypeError(
                f"unsupported types to connect:object1:{object1.__class__,object1},object2:{object2.__class__,object2}"
            )
        return LineSegment(pt1=pt1, pt2=pt2)
