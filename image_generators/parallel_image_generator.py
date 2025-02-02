import math
import random
from typing import List, Tuple

import numpy as np
from shapely.geometry import LineString, Polygon
from entities.line_segment import LineSegment
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
import img_params
from shape_group import ShapeGroup
from util import get_rand_point


class ParallelImageGenerator(ImageGenerator):
    def __init__(self):
        super().__init__()
        # 这里规定不同角度下生成的线段数量范围
        self.alignments = {
            0: [2, 4],
            90: [1, 2],
        }
        # 定义区域为一个矩形：[ (min_x, min_y), (max_x, max_y) ]
        self.region = (
            (GenerationConfig.left_canvas_bound, GenerationConfig.lower_canvas_bound),
            (GenerationConfig.right_canvas_bound, GenerationConfig.upper_canvas_bound),
        )

    def generate(self):
        lines = []
        for rotation in self.alignments:
            num_lines = random.randint(
                self.alignments[rotation][0], self.alignments[rotation][1]
            )
            lines.extend(self.generate_parallel_lines(rotation, num_lines))
        return ShapeGroup([lines])

    def generate_parallel_lines(
        self, angle: float, num_lines: int
    ) -> List[LineSegment]:
        """
        在指定区域内生成一定角度的平行线，
        每条线的中心位置、长度以及与其它线的间距都是随机的。
        """
        min_x, min_y = self.region[0]
        max_x, max_y = self.region[1]

        # 计算区域宽度、高度以及对角线长度，用于确定随机线段的长度范围
        region_width = max_x - min_x
        region_height = max_y - min_y
        region_diag = math.sqrt(region_width**2 + region_height**2)

        # 计算指定角度的方向向量（线段延伸方向）
        angle_rad = math.radians(angle)
        direction = np.array([math.cos(angle_rad), math.sin(angle_rad)])

        lines = []
        for i in range(num_lines):
            # 随机选择一个中心点，位于整个区域内
            center = np.array(
                [random.uniform(min_x, max_x), random.uniform(min_y, max_y)]
            )
            # 随机选择线段长度，范围为区域对角线的 1/4 到 1 倍
            line_length = random.uniform(region_diag / 4, region_diag)
            # 根据中心点和方向向量计算起点和终点
            start = center - (line_length / 2) * direction
            end = center + (line_length / 2) * direction

            # 裁剪线段，使其完全位于定义区域内
            start, end = self.clip_line_to_region(start, end)

            if start is not None and end is not None:
                lines.append(LineSegment(start, end))

        print(f"Generated lines: {lines}")
        return lines

    def clip_line_to_region(
        self, start: np.ndarray, end: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """将线段裁剪到定义的区域内。"""
        min_x, min_y = self.region[0]
        max_x, max_y = self.region[1]

        # 构造整个区域的多边形
        region_polygon = Polygon(
            [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
        )

        # 构造待裁剪的线段
        line = LineString([start, end])
        clipped_line = line.intersection(region_polygon)

        if clipped_line.is_empty:
            print(f"Clipped line is empty: {line}")
            return None, None

        if isinstance(clipped_line, LineString):
            coords = list(clipped_line.coords)
            print(f"Clipped line: {clipped_line}")
            return np.array(coords[0]), np.array(coords[-1])

        if clipped_line.geom_type == "MultiLineString":
            # 如果返回的是 MultiLineString，则选取最长的一段
            longest = max(clipped_line, key=lambda seg: seg.length)
            coords = list(longest.coords)
            print(f"Clipped MultiLineString, selected: {longest}")
            return np.array(coords[0]), np.array(coords[-1])

        print(f"Unexpected clipped line type: {type(clipped_line)}")
        return None, None
