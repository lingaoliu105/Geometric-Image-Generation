import copy
import inspect
from typing import List, Optional, Tuple, Union
import numpy as np
from shapely import LineString, unary_union

from entities.closed_shape import ClosedShape
from entities.complex_shape import ComplexShape
from entities.visible_shape import VisibleShape
from generation_config import GenerationConfig
import img_params
from panel import Panel
from shapely.geometry.base import BaseGeometry
import timeout_decorator
from shapely import Polygon,MultiPolygon

class ShapeGroup:
    def __init__(self, shapes: List[List[VisibleShape]]) -> None:
        self.shapes = shapes if shapes is not None else [[]]

    # @timeout_decorator.timeout(4,use_signals = False)

    def geometry(self, layer) -> BaseGeometry:
        # to keep geometries list updated
        # current_frame = inspect.currentframe()

        # caller_frame = current_frame.f_back
        # # 获取调用者的函数名
        # caller_name = caller_frame.f_code.co_name
        # print(f"Called by function: {caller_name}")
        return unary_union(
            [
                shape.base_geometry
                for shape in self.shapes[layer]
                if isinstance(shape, ClosedShape)
            ]
        )

    def pad_layer(self, layer):
        """make the shape group contain up to the given layer (starting from 0)"""
        while layer >= len(self.shapes):
            self.shapes.append([])

    def add_group(self, new_shapes: Union[List[List[VisibleShape]], "ShapeGroup"]):
        if isinstance(new_shapes, ShapeGroup):
            new_shapes = new_shapes.shapes

        def validate_two_level_list(lst):
            if not isinstance(lst, list):
                raise ValueError("The input must be a list.")

            for item in lst:
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, list):
                            raise ValueError(
                                "The list cannot be nested more than two levels."
                            )

        validate_two_level_list(new_shapes)
        for new_layer, shapes_on_layer in enumerate(new_shapes):
            for shape in shapes_on_layer:
                self.add_shape_on_layer(shape, new_layer)

    def add_shape(self, shape: VisibleShape):
        self.add_shape_on_layer(shape, 0)

    @property
    def layer_num(self):
        return len(self.shapes)

    def add_shape_on_layer(self, shape: VisibleShape, layer: int):
        """layer starts from 0"""
        self.pad_layer(self.layer_num + layer + 1)
        if isinstance(shape, ClosedShape):
            overlapping_group = [[] for _ in range(len(self.shapes))]
            for layer_cnt in range(len(self.shapes)):
                if shape.base_geometry.overlaps(self.geometry(layer_cnt)) and not (
                    shape.base_geometry.contains(self.geometry(layer_cnt))
                    or self.geometry(layer_cnt).contains(shape.base_geometry)
                ):
                    overlapping_group[layer_cnt + layer + 1].extend(
                        ComplexShape.from_overlapping_geometries(
                            shape.base_geometry, self.geometry(layer_cnt)
                        )
                    )

            for layer_cnt, shapes in enumerate(overlapping_group):
                self.shapes[layer_cnt].extend(shapes)
        self.shapes[layer].append(shape)

    def __add__(self, other):
        if isinstance(other, VisibleShape):
            self.add_shape(other)
        elif isinstance(other, ShapeGroup):
            self.add_group(other.shapes)
        elif isinstance(other, list) and all(
            isinstance(item, VisibleShape) for item in other
        ):
            self.add_group([other])
        elif isinstance(other, list) and all(isinstance(item, list) for item in other):
            self.add_group(other)
        else:
            raise ValueError("Unsupported item to add to ShapeGroup")
        return self

    def __len__(self):
        return len(self.shapes)

    def __getitem__(self, key):
        return self.shapes[key]

    def shift(self, offset):
        if not isinstance(offset, np.ndarray):
            offset = np.array(offset)
        for layer in self.shapes:
            for shape in layer:
                shape.shift(offset)

    @property
    def center(self):
        coordinates = [shape.center for shape in self.shapes[0]]
        # 将坐标转换为 numpy 数组
        coords_array = np.array(coordinates)

        # 计算平均值
        avg_x = np.mean(coords_array[:, 0])
        avg_y = np.mean(coords_array[:, 1])

        return np.array([avg_x, avg_y])

    def rotate(self, angle: Union[img_params.Angle, int], origin="center"):
        if origin == "center":
            origin = self.center

        for layer in self.shapes:
            for shape in layer:
                shape.rotate(angle, origin)

    def size(self):
        return sum([len(layer) for layer in self.shapes])

    def scale(self, scale_ratio, origin="center"):
        if origin == "center":
            origin = self.center
        for layer in self.shapes:
            for shape in layer:
                shape.scale(scale_ratio, origin)

    def to_panel(self, top_left, bottom_right):
        """place the shape group in a panel. shape group is by default placed on the entire canvas, and will be shifted and shrinked to fit in the panel"""
        panel_center = (
            (top_left[0] + bottom_right[0]) / 2,
            (top_left[1] + bottom_right[1]) / 2,
        )
        self.shift(panel_center)
        scale_ratio = (bottom_right[0] - top_left[0]) / (
            GenerationConfig.right_canvas_bound - GenerationConfig.left_canvas_bound
        )
        assert scale_ratio == (top_left[1] - bottom_right[1]) / (
            GenerationConfig.upper_canvas_bound - GenerationConfig.lower_canvas_bound
        )
        self.scale(scale_ratio=scale_ratio, origin=panel_center)
        flattened_list = [item for sublist in self.shapes for item in sublist]
        return Panel(
            top_left=top_left,
            bottom_right=bottom_right,
            shapes=flattened_list,
            joints=[],
        )

    def show(self):
        for layer in self.shapes:
            print([f"{shape.__class__.__name__}, uid: {shape.uid}" for shape in layer])

    def flattened(self):
        return [item for sublist in self.shapes for item in sublist]

    def lift_up_layer(self, by: int = 1):
        for _ in range(by):
            self.shapes.insert(0, [])

    def fit_canvas(self):
        while self.exceeds_canvas():
            self.scale(0.9)

    def exceeds_canvas(self):
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

        for layer in self.shapes:
            for shape in layer:
                if shape.base_geometry.intersects(canvas_boundary_geometry):
                    return True
        return False

    def search_size_by_interval(self, other: "ShapeGroup",interval: float):
        """based on layer 0' s geometry"""
        # other_shape = other.geometry(0).buffer(interval)
        # assert other_shape.is_valid
        # while (
        #     not self.roughly_touches(other)
        # ):
        #     self_geometry = self.geometry(0)
        #     if (
        #         self_geometry.overlaps(other_shape)
        #         or self_geometry.intersects(other_shape)
        #         or self_geometry.contains(other_shape)
        #     ):
        #         self.scale(0.5)
        #     else:
        #         self.scale(2.0)
        """based on layer 0's geometry"""
        other_shape = other.geometry(0).buffer(interval)
        assert other_shape.is_valid
        min_scale = 0.1  # 最小缩放比例
        max_scale = 10  # 最大缩放比例
        tolerance = 0.001  # 精度要求
        iteration_count = 0
        max_iterations = 100  # 最大迭代次数
        while abs(max_scale - min_scale) > tolerance:
            own_cpy = copy.deepcopy(self)
            print("adjust")
            if iteration_count >= max_iterations:
                print("Exceeded maximum iterations")
                break

            scale_factor = (min_scale + max_scale) / 2  # 取中间值
            own_cpy.scale(scale_factor)

            if own_cpy.roughly_touches(other):
                print(f"Found a valid scale: {scale_factor}")
                break
            elif own_cpy.geometry(0).overlaps(other_shape) or own_cpy.geometry(0).intersects(other_shape) or own_cpy.geometry(0).contains(other_shape):
                max_scale = scale_factor  # 调整最小缩放比例
            else:
                min_scale = scale_factor  # 调整最大缩放比例

            iteration_count += 1

        self.scale(min_scale)

    def roughly_touches(self, other: "ShapeGroup"):
        tolerance = 0.01
        other_shape = other.geometry(0)
        self_shape = self.geometry(0)
        return (
            self_shape.touches(other_shape)
            or (
                not self_shape.overlaps(other_shape)
                and self_shape.overlaps(other_shape.buffer(tolerance))
            )
            or (
                self_shape.overlaps(other_shape)
                and not self_shape.overlaps(other_shape.buffer(-tolerance))
            )
        )

    def bounds(self,layer=0):
        geom = self.geometry(layer=layer)


        def calculate_bounds(
            geom,
        ) -> Tuple[Tuple[float, float], Tuple[float, float], float, float, float, float]:
            """
            计算 Polygon 或 MultiPolygon 的最左、最右、最高、最低点，
            以及上下高度和左右宽度。

            :param geom: Polygon 或 MultiPolygon
            :return: (最左点, 最右点, 最高点, 最低点, 高度, 宽度)
            """

            if isinstance(geom, MultiPolygon):
                # 对 MultiPolygon 类型，我们需要处理每个子多边形
                all_coords = []
                for polygon in geom:
                    all_coords.extend(list(polygon.exterior.coords))
                    for interior in polygon.interiors:
                        all_coords.extend(list(interior.coords))
            else:
                # 对 Polygon 类型
                all_coords = list(geom.exterior.coords)
                for interior in geom.interiors:
                    all_coords.extend(list(interior.coords))

            # 找到最左、最右、最高、最低的点
            left_point = min(all_coords, key=lambda x: x[0])  # 最左点 (x最小)
            right_point = max(all_coords, key=lambda x: x[0])  # 最右点 (x最大)
            highest_point = max(all_coords, key=lambda x: x[1])  # 最高点 (y最大)
            lowest_point = min(all_coords, key=lambda x: x[1])  # 最低点 (y最小)

            # 计算高度和宽度
            height = highest_point[1] - lowest_point[1]  # 高度 = 最高点的y - 最低点的y
            width = right_point[0] - left_point[0]  # 宽度 = 最右点的x - 最左点的x

            return left_point, right_point, highest_point, lowest_point, height, width

        return calculate_bounds(geom)