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
from shapely import Polygon, MultiPolygon
from shapely.geometry import ( 
    Point,
    LinearRing,
    MultiLineString,
    GeometryCollection, 
)


class ShapeGroup:
    def __init__(self, shapes: List[List[VisibleShape]]) -> None:
        self.shapes = shapes if shapes is not None else [[]]

    def geometry(self, layer, include_1d = False) -> BaseGeometry:
        return unary_union(
            [
                shape.base_geometry
                for shape in self.shapes[layer]
                if isinstance(shape, ClosedShape) or include_1d
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
        while len(self.shapes[-1])==0: # remove unused layers
            self.shapes.pop()

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
        panel_center = (
            (top_left[0] + bottom_right[0]) / 2,
            (top_left[1] + bottom_right[1]) / 2,
        )
        self.shift(panel_center)
        
        # 计算初始缩放比例，使用更大的初始值
        scale_ratio = min(
            abs(bottom_right[0] - top_left[0]) / GenerationConfig.canvas_width,
            abs(bottom_right[1] - top_left[1]) / GenerationConfig.canvas_height,
        ) * 0.95  # 增加初始系数到0.95
        
        self.scale(scale_ratio=scale_ratio, origin=panel_center)
        
        # 创建面板边界
        panel_polygon = Polygon([
            (top_left[0], top_left[1]),
            (bottom_right[0], top_left[1]),
            (bottom_right[0], bottom_right[1]),
            (top_left[0], bottom_right[1])
        ])
        
        # 使用更温和的缩放因子
        max_attempts = 10  # 减少最大尝试次数
        attempt = 0
        scale_factor = 0.95  # 更温和的缩放因子
        
        while attempt < max_attempts:
            fits = True
            for layer in self.shapes:
                for shape in layer:
                    if not shape.base_geometry.within(panel_polygon):
                        fits = False
                        break
                if not fits:
                    break
                
            if fits:
                break
                
            self.scale(scale_factor, origin=panel_center)
            attempt += 1
            
            # 如果多次尝试后仍然不适应，才使用更激进的缩放
            if attempt > 5:
                scale_factor = 0.9
        
        flattened_list = [item for sublist in self.shapes for item in sublist]
        return Panel(
            top_left=top_left,
            bottom_right=bottom_right,
            shapes=flattened_list,
            joints=[],
        )

    def show(self):
        for layer in self.shapes:
            print([f"{shape.__class__.__name__},{shape.shape}, uid: {shape.uid}" for shape in layer])

    def flattened(self):
        return [item for sublist in self.shapes for item in sublist]

    def lift_up_layer(self, by: int = 1):
        for _ in range(by):
            self.shapes.insert(0, [])

    def fit_canvas(self):
        while self.exceeds_canvas():
            self.scale(0.8)

    def exceeds_canvas(self):
        # 创建画布边界多边形而不是线段
        canvas_polygon = Polygon([
            (GenerationConfig.right_canvas_bound, GenerationConfig.upper_canvas_bound),
            (GenerationConfig.left_canvas_bound, GenerationConfig.upper_canvas_bound),
            (GenerationConfig.left_canvas_bound, GenerationConfig.lower_canvas_bound),
            (GenerationConfig.right_canvas_bound, GenerationConfig.lower_canvas_bound)
        ])
    
        for layer in self.shapes:
            for shape in layer:
                geom = shape.base_geometry
                # 检查是否完全在画布内
                if not geom.within(canvas_polygon):
                    return True
        return False
    
        def fit_canvas(self):
            max_attempts = 100  # 防止无限循环
            attempt = 0
            scale_factor = 0.9  # 每次缩小10%
            
            while self.exceeds_canvas() and attempt < max_attempts:
                self.scale(scale_factor)
                attempt += 1
                # 如果多次缩放后仍然超出，增加缩放强度
                if attempt > 10:
                    scale_factor = 0.8

    def search_size_by_interval(self, other: "ShapeGroup", interval: float):
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
            if iteration_count >= max_iterations:
                print("Exceeded maximum iterations")
                break

            scale_factor = (min_scale + max_scale) / 2  # 取中间值
            own_cpy.scale(scale_factor)

            if own_cpy.roughly_touches(other):
                print(f"Found a valid scale: {scale_factor}")
                break
            elif (
                own_cpy.geometry(0).overlaps(other_shape)
                or own_cpy.geometry(0).intersects(other_shape)
                or own_cpy.geometry(0).contains(other_shape)
            ):
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

    def bounds(self, layer=0):
        geom = self.geometry(layer=layer, include_1d=True)

        def extract_coordinates(geometry):
            """递归提取所有几何对象的坐标"""
            coords = []
            if geometry.is_empty:
                return coords
                
            if isinstance(geometry, (Point)):
                coords.append((geometry.x, geometry.y))
            elif isinstance(geometry, (LineString, LinearRing)):
                coords.extend(list(geometry.coords))
            elif isinstance(geometry, (Polygon)):
                coords.extend(list(geometry.exterior.coords))
                for interior in geometry.interiors:
                    coords.extend(list(interior.coords))
            elif isinstance(geometry, (MultiPolygon, MultiLineString, GeometryCollection)):
                for geom in geometry.geoms:
                    coords.extend(extract_coordinates(geom))
            return coords

        def calculate_bounds(geom):
            """通用边界计算方法"""
            if geom.is_empty:
                return ((0,0), (0,0), (0,0), (0,0), 0, 0)

            # 提取所有坐标（支持任意几何类型）
            all_coords = extract_coordinates(geom)
            
            if not all_coords:  # 处理空几何的情况
                return ((0,0), (0,0), (0,0), (0,0), 0, 0)

            # 找到极值点
            left_point = min(all_coords, key=lambda x: x[0])
            right_point = max(all_coords, key=lambda x: x[0])
            highest_point = max(all_coords, key=lambda x: x[1])
            lowest_point = min(all_coords, key=lambda x: x[1])

            # 计算尺寸
            height = highest_point[1] - lowest_point[1]
            width = right_point[0] - left_point[0]

            return (tuple(left_point), 
                    tuple(right_point), 
                    tuple(highest_point), 
                    tuple(lowest_point), 
                    height, 
                    width)
