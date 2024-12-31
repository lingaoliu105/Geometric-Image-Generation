import copy
import random
import sys
from networkx import center
import numpy as np
from shapely import LineString, Point
from common_types import *
from typing import Literal, Optional, Union

from entities.visible_shape import OpenShape, VisibleShape
import generation_config
import img_params
from tikz_converters import LineSegmentConverter
from util import (
    almost_equal,
    generate_random_points_around_point,
    get_line_rotation,
    get_point_distance,
    get_rand_point,
    rotate_point,
)
from shapely.affinity import translate
from shapely.ops import nearest_points


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
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
    ) -> None:
        super().__init__(tikz_converter=LineSegmentConverter())
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

        self.color = (
            color if color is not None else random.choice(list(img_params.Color))
        )
        self.lightness = (
            lightness
            if lightness is not None
            else random.choice(list(img_params.Lightness))
        )
        self.is_expanded = False
        
    @property
    def base_geometry(self):
        if self.is_expanded:
            return self._base_geometry_expanded
        else:
            return self._base_geometry
        
    @staticmethod
    def within_distance(point:Coordinate, distance:float):
        pt1,pt2 = generate_random_points_around_point(center=point,distance=distance)
        ls = LineSegment(pt1,pt2)
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
        if almost_equal(length,0.0):
            pass
        elif length > 0:
            if self.is_expanded: # reset if already expanded before
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

    def adjust_by_interval(
        self,
        other: VisibleShape,
        interval: float,
        prior_method: Literal["rotate", "scale"],
    ):
        other_copy = other.copy
        mid_point = Point(self.center)
        if prior_method == "rotate":
            maximum_achievable_distance = mid_point.distance(other.base_geometry)
            minimum_achievable_distance = maximum_achievable_distance - self.radius
            if maximum_achievable_distance < interval:
                print("interval too large", file=sys.stderr)
                return
            nearest_point_on_shape, _ = nearest_points(
                other_copy.base_geometry, mid_point
            )
            perpendicular_line_rotation = get_line_rotation(
                nearest_point_on_shape.coords[0], self.center
            )
            if (
                minimum_achievable_distance <= interval
            ):  # the interval is achievable with rotation
                upper, lower = perpendicular_line_rotation, self.rotation
                while (
                    abs(upper - lower)
                    > generation_config.GenerationConfig.search_threshhold
                ):
                    mid = (upper + lower) / 2
                    self.rotate(self.center, mid - self.rotation)
                    distance = self._base_geometry.distance(other_copy.base_geometry)
                    if distance > interval:
                        lower = mid
                    else:
                        upper = mid
            else:
                self.rotate(self.center, perpendicular_line_rotation - self.rotation)

        else:
            return

    # def adjust_by_scaling(self,other:VisibleShape,interval:float,pivot:Coordinate):
    #     # if almost_equal(pivot,self.endpt_up) or almost_equal(pivot,self.endpt_down):
    #     # check if the desired interval is achievable by simply scaling
    #     cpy = self.copy
    #     cpy.scale_with_pivot((generation_config.GenerationConfig.canvas_height + generation_config.GenerationConfig.canvas_width)*10/cpy.length)
    #     minimum_achievable_distance = cpy.base_geometry.distance(other.base_geometry)
    #     if minimum_achievable_distance <= interval:
    #         min_ratio =
