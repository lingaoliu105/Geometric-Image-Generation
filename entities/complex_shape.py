from collections import defaultdict
import random
from typing import List, Optional

import shapely
from entities.closed_shape import ClosedShape
from entities.entity import Relationship
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
    def arbitrary_rectangle(aspect_ratio=None):
        """return a rectangle with specified or default aspect ratio"""
        if aspect_ratio is None:
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
    def arbitrary_right_triangle(aspect_ratio=None):
        """return a right triangle with specified or default aspect ratio"""
        if aspect_ratio is None:
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
        def generate_orthogonal_polygon_by_cells(start_pos=None, selection_order="random"):
        
            def generate_polyomino(n_cells, start_pos=(0,0), selection_order="random"):
                """
                Generate a polyomino with n_cells cells using deterministic cell selection.
                Each cell is represented by its bottom-left coordinate (x, y).
                """
                polyomino = set()
                polyomino.add(start_pos)
                
                # frontier: cells adjacent to current polyomino but not yet added
                frontier = set()
                def add_neighbors(cell):
                    x, y = cell
                    neighbors = []
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nbr = (x+dx, y+dy)
                        if nbr not in polyomino:
                            neighbors.append(nbr)
                    if selection_order == "sequential":
                        # Sort neighbors for deterministic selection
                        neighbors.sort(key=lambda p: (p[1], p[0]))
                    for nbr in neighbors:
                        frontier.add(nbr)
                
                add_neighbors(start_pos)
                
                while len(polyomino) < n_cells and frontier:
                    if selection_order == "sequential":
                        # Choose the leftmost-bottommost cell
                        cell = min(frontier, key=lambda p: (p[1], p[0]))
                    else:
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
                max_try = 1000
                cnt=0
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
                    cnt+=1
                    if cnt>max_try:
                        raise TimeoutError()

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
            flag=True
            while flag:
                try:
                    polyomino = generate_polyomino(GenerationConfig.arbitrary_shape_cell_num)
                    edges = get_boundary_edges(polyomino)
                    polygon = chain_edges_to_polygon(edges)
                    vertices = merge_collinear(polygon)
                    flag = False
                except TimeoutError:
                    continue
            return vertices
           

        vertices = generate_orthogonal_polygon_by_cells()
                        
        return ComplexShape(geometry=shapely.Polygon(vertices))

    @property
    def center(self):
        try:
            return self._base_geometry.centroid.coords[0]
        except IndexError:
            print("irregular center!",self, self.base_geometry)
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
