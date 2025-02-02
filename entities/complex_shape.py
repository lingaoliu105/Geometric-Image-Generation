from collections import defaultdict
import math
import random
from typing import List, Literal, Optional, Set, Tuple

from matplotlib.pyplot import isinteractive
import numpy as np
import shapely
from entities.closed_shape import ClosedShape
from entities.entity import Relationship
from entities.line_segment import LineSegment
from generation_config import GenerationConfig
import img_params
from tikz_converters import ComplexShapeConverter
from shapely.affinity import scale
from shapely.geometry.base import BaseMultipartGeometry


class ComplexShape(ClosedShape, Relationship):
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
        "position",
        "base_geometry",
    ] + dataset_annotation_categories

    def __init__(
        self,
        color: Optional[img_params.Color] = None,
        pattern: Optional[img_params.Pattern] = None,
        lightness: Optional[img_params.Lightness] = None,
        outline=None,
        outline_lightness=None,
        pattern_color=None,
        pattern_lightness=None,
        outline_color=None,
        outline_thickness=None,
        geometry: shapely.geometry.base.BaseGeometry = None,
    ) -> None:
        super().__init__(
            tikz_converter=ComplexShapeConverter(),
            color=color,
            lightness=lightness,
            outline=outline,
            outline_color=outline_color,
            outline_lightness=outline_lightness,
            outline_thickness=outline_thickness,
            pattern=pattern,
            pattern_color=pattern_color,
            pattern_lightness=pattern_lightness,
        )
        self.is_expanded = False
        self.shape = img_params.Shape.arbitrary
        if geometry is not None:
            self._base_geometry = geometry

    @staticmethod
    def from_overlapping_geometries(
        geom1: shapely.geometry.base.BaseGeometry,
        geom2: shapely.geometry.base.BaseGeometry,
    ) -> List["ComplexShape"]:
        if (
            isinstance(geom1, shapely.LineString)
            or isinstance(geom2, shapely.LineString)
            or isinstance(geom1, shapely.MultiLineString)
            or isinstance(geom2, shapely.MultiLineString)
        ):
            return []
        overlaping_base_geometry = geom1.intersection(geom2)
        if isinstance(overlaping_base_geometry, BaseMultipartGeometry):
            overlapping_geoms = list(overlaping_base_geometry.geoms)
        else:
            overlapping_geoms = [overlaping_base_geometry]
        overlaps = [
            ComplexShape(geometry=geom)
            for geom in overlapping_geoms
            if isinstance(geom, shapely.Polygon) and not geom.is_empty
        ]
        for i in range(len(overlaps)):
            overlaps[i].shape = img_params.Type.INTERSECTIONREGION
        return overlaps

    @staticmethod
    def arbitrary_rectangle():
        """return a rectangle, aspect ratio between 1 to 3, and size occupying canvas"""
        aspect_ratio = random.uniform(1, 3)
        length = min(GenerationConfig.canvas_height, GenerationConfig.canvas_width)
        width = length / aspect_ratio
        shape = ComplexShape(
            geometry=shapely.Polygon(
                [
                    (length / 2, width / 2),
                    (-length / 2, width / 2),
                    (-length / 2, -width / 2),
                    (length / 2, -width / 2),
                ]
            )
        )
        shape.shape = img_params.Shape.rectangle
        return shape

    @staticmethod
    def arbitrary_right_triangle():
        aspect_ratio = random.uniform(1, 3)
        length = min(GenerationConfig.canvas_height, GenerationConfig.canvas_width)
        width = length / aspect_ratio
        shape = ComplexShape(
            geometry=shapely.Polygon(
                [
                    (length / 2, width / 2),
                    (-length / 2, width / 2),
                    (-length / 2, -width / 2),
                ]
            )
        )
        shape.shape = img_params.Shape.triangle_rt
        return shape

    @staticmethod
    def arbitrary_polygon():
        def generate_orthogonal_polygon_by_cells():
        
            def generate_polyomino(n_cells, seed=None):
                """
                随机生成一个由 n_cells 个单元格构成的多胞形（polyomino），
                每个单元格由其左下角坐标 (x, y) 表示。
                """
                if seed is not None:
                    random.seed(seed)
                
                polyomino = set()
                polyomino.add((0, 0))
                
                # frontier: 与当前多胞形邻接且尚未加入的格子
                frontier = set()
                def add_neighbors(cell):
                    x, y = cell
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nbr = (x+dx, y+dy)
                        if nbr not in polyomino:
                            frontier.add(nbr)
                
                add_neighbors((0,0))
                
                while len(polyomino) < n_cells and frontier:
                    cell = random.choice(list(frontier))
                    polyomino.add(cell)
                    frontier.remove(cell)
                    add_neighbors(cell)
                
                return polyomino

            def get_boundary_edges(polyomino):
                """
                给定多胞形（格子集合），返回边界上的所有边段。
                每个边段表示为 ((x1, y1), (x2, y2))。
                """
                edges = []
                for (x, y) in polyomino:
                    # 对于每个单元格，检查4个方向的边
                    # 底边：如果 (x, y-1) 不在 polyomino，则底边是外边界
                    if (x, y-1) not in polyomino:
                        edges.append(((x, y), (x+1, y)))
                    # 右边：检查 (x+1, y)
                    if (x+1, y) not in polyomino:
                        edges.append(((x+1, y), (x+1, y+1)))
                    # 顶边：检查 (x, y+1)
                    if (x, y+1) not in polyomino:
                        edges.append(((x+1, y+1), (x, y+1)))
                    # 左边：检查 (x-1, y)
                    if (x-1, y) not in polyomino:
                        edges.append(((x, y+1), (x, y)))
                
                return edges

            def chain_edges_to_polygon(edges):
                """
                将一组边段链化成一个闭合多边形的顶点序列。
                假设边段构成一条单闭合曲线，每个顶点度为2。
                """
                # 构造：从一个顶点到与之相连的边段列表
                conn = {}
                for seg in edges:
                    a, b = seg
                    for v1, v2 in [(a, b), (b, a)]:
                        conn.setdefault(v1, []).append(v2)
                
                # 任选一个起始顶点（例如最左下角的点）
                start = min(conn.keys(), key=lambda v: (v[1], v[0]))  # 按 y 然后 x 排序
                polygon = [start]
                current = start
                prev = None
                while True:
                    nbrs = conn[current]
                    # 由于度为2（起始点除外），选择一个不是上一步的顶点即可
                    if prev is None:
                        next_v = nbrs[0]
                    else:
                        if nbrs[0] == prev:
                            next_v = nbrs[1]
                        else:
                            next_v = nbrs[0]
                    if next_v == start:
                        break
                    polygon.append(next_v)
                    prev, current = current, next_v

                return polygon

            def merge_collinear(polygon):
                """
                对顶点序列做合并：如果连续三个点共线，则去除中间点。
                """
                if len(polygon) < 3:
                    return polygon
                merged = []
                n = len(polygon)
                for i in range(n):
                    p_prev = polygon[i - 1]
                    p_curr = polygon[i]
                    p_next = polygon[(i + 1) % n]
                    # 由于边都是水平或垂直，判断共线可以直接判断坐标相同
                    if p_prev[0] == p_curr[0] == p_next[0] or p_prev[1] == p_curr[1] == p_next[1]:
                        # p_curr 在一条直线上，可省略
                        continue
                    else:
                        merged.append(p_curr)
                return merged
            polyomino = generate_polyomino(20)
            edges = get_boundary_edges(polyomino)
            polygon = chain_edges_to_polygon(edges)
            vertices = merge_collinear(polygon)
            return vertices
        
            """
            生成一个由垂直和水平线段组成的简单多边形（不自交）
            
            参数:
                min_vertices: 最少顶点数
                max_vertices: 最多顶点数
            
            返回:
                顶点坐标列表，按顺序连接即可形成多边形
            """
            
            def is_valid_next_point(points: List[Tuple[int, int]], next_point: Tuple[int, int],
                                occupied: Set[Tuple[int, int]]) -> bool:
                """检查新点是否会导致多边形自交"""
                if not points:
                    return True
                    
                current = points[-1]
                # 检查新的线段是否与已有线段相交
                if next_point in occupied:
                    return False
                    
                # 检查路径上的点是否被占用
                if current[0] == next_point[0]:  # 垂直线段
                    y_min = min(current[1], next_point[1])
                    y_max = max(current[1], next_point[1])
                    for y in range(y_min + 1, y_max):
                        if (current[0], y) in occupied:
                            return False
                else:  # 水平线段
                    x_min = min(current[0], next_point[0])
                    x_max = max(current[0], next_point[0])
                    for x in range(x_min + 1, x_max):
                        if (x, current[1]) in occupied:
                            return False
                            
                return True

            def get_possible_directions(current: Tuple[int, int], occupied: Set[Tuple[int, int]], 
                                    start_point: Tuple[int, int], points_count: int) -> List[Tuple[int, int]]:
                """获取可能的下一步方向"""
                directions = []
                # 可能的移动方向：上、下、左、右
                moves = [(0, 1), (0, -1), (-1, 0), (1, 0)]
                
                for dx, dy in moves:
                    # 随机选择移动距离（1到5个单位）
                    distance = random.randint(1, 5)
                    next_point = (current[0] + dx * distance, current[1] + dy * distance)
                    
                    # 如果已经有足够的点，检查是否可以回到起点
                    if points_count >= min_vertices - 1 and next_point == start_point:
                        if is_valid_next_point(points, next_point, occupied):
                            directions.append(next_point)
                    # 否则添加新的有效点
                    elif is_valid_next_point(points, next_point, occupied):
                        directions.append(next_point)
                        
                return directions

            # 主算法开始
            points = []
            occupied = set()
            
            # 从原点开始
            start_point = (0, 0)
            current = start_point
            points.append(current)
            occupied.add(current)
            
            while len(points) < max_vertices:
                possible_next = get_possible_directions(current, occupied, start_point, len(points))
                
                # 如果没有可行的下一步，且已达到最小顶点数要求，尝试闭合多边形
                if not possible_next and len(points) >= min_vertices:
                    # 尝试直接连回起点
                    if is_valid_next_point(points, start_point, occupied):
                        points.append(start_point)
                        break
                        
                # 如果没有可行的下一步，且未达到最小顶点数，则重新开始
                if not possible_next:
                    return generate_orthogonal_polygon(min_vertices, max_vertices)
                    
                # 随机选择下一个点
                next_point = random.choice(possible_next)
                points.append(next_point)
                occupied.add(next_point)
                current = next_point
                
                # 如果回到起点，结束算法
                if next_point == start_point:
                    break
            
            return points
        
            """
            生成一个不自交的正交多边形
            
            参数:
            min_size: 最小转角数量
            max_size: 最大转角数量
            grid_size: 网格大小
            
            返回:
            vertices: 多边形顶点坐标列表 [(x1,y1), (x2,y2), ...]
            """
            def is_valid_step(curr_x, curr_y, direction, occupied):
                """检查下一步是否有效"""
                next_x, next_y = curr_x, curr_y
                if direction == 0:  # 右
                    next_x += 1
                elif direction == 1:  # 上
                    next_y += 1
                elif direction == 2:  # 左
                    next_x -= 1
                else:  # 下
                    next_y -= 1
                    
                # 检查是否在网格内
                if not (0 <= next_x < grid_size and 0 <= next_y < grid_size):
                    return False
                    
                # 检查是否已被占用
                if (next_x, next_y) in occupied:
                    return False
                    
                return True

            def can_close_polygon(curr_x, curr_y, start_x, start_y, direction, vertices):
                """检查是否可以闭合多边形"""
                if len(vertices) < min_size:
                    return False
                    
                # 检查是否可以通过一次或两次转向回到起点
                if direction == 0:  # 当前向右
                    if curr_y == start_y and curr_x < start_x:
                        return True
                    if curr_x < start_x:
                        return (curr_x, start_y) not in vertices
                elif direction == 1:  # 当前向上
                    if curr_x == start_x and curr_y < start_y:
                        return True
                    if curr_y < start_y:
                        return (start_x, curr_y) not in vertices
                elif direction == 2:  # 当前向左
                    if curr_y == start_y and curr_x > start_x:
                        return True
                    if curr_x > start_x:
                        return (curr_x, start_y) not in vertices
                else:  # 当前向下
                    if curr_x == start_x and curr_y > start_y:
                        return True
                    if curr_y > start_y:
                        return (start_x, curr_y) not in vertices
                return False

            # 主算法开始
            while True:
                # 随机选择起点
                start_x = random.randint(1, grid_size-2)
                start_y = random.randint(1, grid_size-2)
                vertices = [(start_x, start_y)]
                occupied = {(start_x, start_y)}
                
                curr_x, curr_y = start_x, start_y
                direction = random.randint(0, 3)  # 0:右, 1:上, 2:左, 3:下
                
                while len(vertices) < max_size:
                    # 尝试继续当前方向
                    if is_valid_step(curr_x, curr_y, direction, occupied):
                        if direction == 0:
                            curr_x += 1
                        elif direction == 1:
                            curr_y += 1
                        elif direction == 2:
                            curr_x -= 1
                        else:
                            curr_y -= 1
                            
                        vertices.append((curr_x, curr_y))
                        occupied.add((curr_x, curr_y))
                        
                        # 检查是否可以闭合多边形
                        if can_close_polygon(curr_x, curr_y, start_x, start_y, direction, vertices):
                            # 添加闭合路径的顶点
                            if curr_x != start_x:
                                vertices.append((start_x, curr_y))
                            if curr_y != start_y:
                                vertices.append((start_x, start_y))
                            return vertices
                    else:
                        # 转向
                        direction = (direction + 1) % 4
                        
                # 如果当前尝试失败，重新开始
                continue

        vertices = generate_orthogonal_polygon_by_cells()
                        
        return ComplexShape(geometry=shapely.Polygon(vertices))

    @property
    def center(self):
        try:
            return self._base_geometry.centroid.coords[0]
        except IndexError:
            print(self, self.base_geometry)
            return self._base_geometry.boundary.coords[0]

    @property
    def position(self):
        return self.center

    def expand(self, ratio):
        self._base_geometry = scale(
            self._base_geometry, xfact=ratio, yfact=ratio, origin="center"
        )
        return self

    def expand_fixed(self, length):
        cpy = self.copy
        cpy._base_geometry = self._base_geometry.buffer(length)
        return cpy
