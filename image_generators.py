"""
合并的 image_generators 模块
包含所有图像生成器类和相关函数
"""

import random
import re
# === 通用导入 ===
from abc import ABC, abstractmethod
from typing import Dict, List

import numpy as np
import shapely
from shapely import LineString, Point

import generation_config
import img_params
# === 项目相关导入 ===
from common_types import *
from entities.closed_shape import ClosedShape
from entities.complex_shape import ComplexShape
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from generation_config import (GenerationConfig,
                               step_into_config_scope_decorator,
                               step_out_config_scope)
from input_configs import SimpleImageConfig
from shape_group import ShapeGroup
from util import *

# === 基类 ImageGenerator ===

# to apply decorators written in base class to subclasses
def get_decorators_from_method(method):
    """尝试从方法中提取装饰器"""
    decorators = []

    # 如果是 functools.wraps 包装过的方法，递归提取
    current = method
    while hasattr(current, "__wrapped__"):
        decorators.append(current.__wrapped__)
        current = getattr(current, "__wrapped__", None)
    return decorators[::-1]  # 保持装饰器顺序


class AutoInheritDecoratorMeta(type):
    def __new__(cls, name, bases, attrs):
        # 创建新类之前，先处理方法
        for method_name, method in attrs.items():
            if callable(method) and not method_name.startswith("__"):
                
                
                # 收集所有父类中该方法的装饰器
                inherited_decorators = set()
                for base in reversed(bases):  # 从最远的祖先开始找
                    base_method = getattr(base, method_name, None)
                    if base_method and hasattr(base_method, "__wrapped__"):
                        inherited_decorators.update(
                            get_decorators_from_method(base_method)
                        )

                # 应用收集到的装饰器
                for decorator in inherited_decorators:
                    if decorator.__name__ == "step_into_config_scope" or decorator.__name__ == "step_out_config_scope":
                        method = decorator(method)
                attrs[method_name] = method

        return super().__new__(cls, name, bases, attrs)


class ImageGenerator(metaclass=AutoInheritDecoratorMeta):

    # @step_into_config_scope_decorator
    def __init__(self) -> None:
        self.shapes:ShapeGroup = ShapeGroup([[]])
        child_class_name = self.__class__.__name__
        if child_class_name.endswith("Generator"):
            child_class_name = child_class_name[:-9]

        def camel_to_snake(camel_str: str) -> str:
            """
            Convert a camel case string to snake case.
            
            :param camel_str: The camel case string to convert.
            :return: The snake case string.
            """
            # Use regular expression to insert underscores before uppercase letters and convert to lowercase
            snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
            return snake_str
        # Convert camel case to snake case
        snake_str = camel_to_snake(child_class_name)

        # Add _config suffix
        config_name = f"{snake_str}_config"
        try:
            self.distribution_dict = getattr(GenerationConfig,config_name)["sub_composition_distribution"]
        except (KeyError,TypeError) as e:
            self.distribution_dict  = {}
        if self.distribution_dict=={}:
            self.distribution_dict = {"simple":1.0}
    @abstractmethod
    @step_out_config_scope
    def generate(self)->ShapeGroup:
        pass

    @property
    def panel_center(self):
        return (self.panel_bottom_right+self.panel_top_left) / 2

    @property
    def panel_radius(self):
        return np.linalg.norm(self.panel_bottom_right - self.panel_top_left) / 2


# === SimpleImageGenerator ===


class SimpleImageGenerator(ImageGenerator):
    """
    Generate single elements like SimpleShape or LineSegment and return as ShapeGroup
    No further sub elements
    """

    def __init__(self) -> None:
        super().__init__()
        self.shape_distribution = GenerationConfig.shape_distribution
        self.config: SimpleImageConfig = GenerationConfig.simple_image_config

    def generate(self) -> ShapeGroup:
        """generate a single element with deterministic configuration"""
        shape = random.choices(
            list(img_params.Shape), weights=self.shape_distribution, k=1
        )[0]

        if shape == img_params.Shape.linesegment:
            element = LineSegment(
                pt1=(-GenerationConfig.canvas_limit / 2, 0),
                pt2=(GenerationConfig.canvas_limit / 2, 0),
            )
        elif shape == img_params.Shape.rectangle:
            aspect_ratio = random.uniform(
                self.config.aspect_ratio.min, self.config.aspect_ratio.max
            )
            element = ComplexShape.arbitrary_rectangle(aspect_ratio=aspect_ratio)
        elif shape == img_params.Shape.triangle_rt:
            aspect_ratio = random.uniform(
                self.config.aspect_ratio.min, self.config.aspect_ratio.max
            )
            element = ComplexShape.arbitrary_right_triangle(aspect_ratio=aspect_ratio)
        elif shape == img_params.Shape.arbitrary:
            element = ComplexShape.arbitrary_polygon()
        else:
            element = SimpleShape(
                position=(0, 0),
                shape=shape,
                size=min(GenerationConfig.canvas_width, GenerationConfig.canvas_height)
                / 2,
                rotation=img_params.Angle.deg0,
            )
        self.shapes.add_shape(element)
        return self.shapes


# === ChainingImageGenerator ===

class ChainingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.position: Coordinate = (0, 0)
        # TODO: combine the chain linesegments into one entity for json labelling

        # TODO: add default value when some configs are not given by user
        self.draw_chain = generation_config.GenerationConfig.chaining_image_config.draw_chain
        self.chain_shape = generation_config.GenerationConfig.chaining_image_config.chain_shape
        self.element_num = GenerationConfig.chaining_image_config.element_num
        self.interval = GenerationConfig.chaining_image_config.interval
        self.chain = []  # initial positions of each element
        self.rotation = GenerationConfig.chaining_image_config.rotation
        self.chain_level = GenerationConfig.chaining_image_config.chain_level
        self.skipped = {}

    def generate_chain(self):
        assert self.element_num >= 2 and self.element_num <= 20
        # composite the image first, then shift to the center pos
        if self.chain_shape == "bezier":
            curve_function = lambda: generate_random_bezier_curve()
        elif self.chain_shape == "circle":
            curve_function = lambda: generate_circle_curve(random.randrange(4, 8))
        elif self.chain_shape == "line":
            curve_function = lambda: get_points_on_line(
                (-GenerationConfig.canvas_limit / 2, 0.0),
                (GenerationConfig.canvas_limit / 2, 0.0),
            )
        else:
            print("curve type not assigned")
            raise
        self.curve_point_set = curve_function()
        self.curve_point_set = [
            rotate_point(pt, (0, 0), self.rotation) for pt in self.curve_point_set
        ]

        def get_chain():
            step_length = max(1, len(self.curve_point_set) // (self.element_num - 1))
            chain = [
                self.curve_point_set[
                    min(step_length * index, len(self.curve_point_set) - 1)
                ]
                for index in range(self.element_num)
            ]  # the set of all centers of the element shapes
            return chain

        self.chain = get_chain()

    def generate_shapes_on_chain(self):
        prev_elements = None
        for i in range(self.element_num):
            # skip if current center is already covered by the previous shape
            if i > 0 and shapely.Point(self.chain[i]).within(
                self.shapes.geometry(0).buffer(self.interval)
            ):
                # 跳过位置时正确设置前后连接关系
                self.skipped[i] = {"prev": prev_elements, "next": None}
                continue


            element_grp = generate_shape_group()
            element_grp.shift(self.chain[i] - element_grp.center)
            element_grp.scale(1 / self.element_num)
            element_grp.scale(1 - self.interval / GenerationConfig.canvas_limit / 2)
            element_grp.rotate(angle=random.choice(list(img_params.Angle)))

            # 处理LineString类型的特殊情况
            if isinstance(element_grp.geometry(0, include_1d=True), LineString):
                self.skipped[i] = {"prev": prev_elements, "next": None}
                prev_elements = None
                continue

            # 处理形状重叠和大小调整
            if i > 0 and any(
                [isinstance(shape, ClosedShape) for shape in element_grp[0]]
            ):
                if prev_elements is not None:
                    prev_geometry = prev_elements.geometry(0, include_1d=True)
                    if not isinstance(prev_geometry, LineString):
                        while not (
                            element_grp.geometry(0).overlaps(prev_geometry)
                            or element_grp.geometry(0).contains(prev_geometry)
                        ):
                            element_grp.scale(
                                2
                            )  # expand new shape to make sure it overlaps prev to guarantee size search result
                        element_grp.search_size_by_interval(
                            prev_elements, self.interval
                        )

                # 更新上一个被跳过位置的next连接
                for j in range(i - 1, -1, -1):
                    if j in self.skipped and self.skipped[j]["next"] is None:
                        self.skipped[j]["next"] = element_grp
                        break

            prev_elements = element_grp
            self.shapes.add_group(element_grp)

    def fill_connecting_line_segments(self):
        # 处理过的索引，避免重复处理
        processed_indices = set()

        for start_index in sorted(self.skipped.keys()):
            if start_index in processed_indices:
                continue

            # 获取前一个形状
            prev_shape = self.skipped[start_index].get("prev")
            if prev_shape is None:
                start_point = Point(self.chain[start_index])
            else:
                start_point = prev_shape.geometry(0)

            # 收集连续的被跳过元素
            current_index = start_index
            consecutive_skipped = []

            while current_index in self.skipped:
                consecutive_skipped.append(current_index)
                processed_indices.add(current_index)
                current_index += 1

            # 获取下一个形状
            last_skipped_index = consecutive_skipped[-1]
            next_shape = self.skipped[last_skipped_index].get("next")

            if next_shape is None:
                # 如果没有下一个形状，使用链中的位置作为终点
                end_point = Point(self.chain[last_skipped_index])
            else:
                end_point = next_shape.geometry(0)

            # 如果只有一个被跳过的元素，直接创建一条连接线
            if len(consecutive_skipped) == 1:
                self.shapes.add_shape(LineSegment.connect(start_point, end_point))
            else:
                # 创建经过中间点的连接线段
                current_point = start_point
                for i in range(len(consecutive_skipped) - 1):
                    idx = consecutive_skipped[i]
                    next_idx = consecutive_skipped[i + 1]
                    # 使用两个跳过点之间的中点作为连接点
                    midpoint = LineString(
                        [self.chain[idx], self.chain[next_idx]]
                    ).interpolate(0.5)
                    self.shapes.add_shape(LineSegment.connect(current_point, midpoint))
                    current_point = midpoint

                # 连接最后一个中间点到终点
                self.shapes.add_shape(LineSegment.connect(current_point, end_point))

    def add_chain_segments(self):
        chain_segments = [
            LineSegment(
                self.curve_point_set[i],
                self.curve_point_set[i + 1],
                color=img_params.Color.black,
            )
            for i in range(len(self.curve_point_set) - 2)
            # for i in range(0,len(self.curve_point_set) - 2,2)
        ]

        if self.chain_level == "bottom":
            self.shapes.lift_up_layer()
            for seg in chain_segments:
                self.shapes.add_shape_on_layer(seg, 0)
        elif self.chain_level == "top":
            top_layer = self.shapes.layer_num - 1
            for seg in chain_segments:
                self.shapes.add_shape_on_layer(seg, top_layer)
        else:
            raise ValueError()

    def generate(self) -> ShapeGroup:
        """generate a composite geometry entity by chaining simple shapes

        Args:
            position (numpy 2-d array): coordinate of the center of the chained shape
            rotation (float): rotation of the overall composite chained shapes in degree
        """
        self.generate_chain()
        self.generate_shapes_on_chain()
        self.fill_connecting_line_segments()
        if self.draw_chain:
            self.add_chain_segments()
        self.shapes.fit_canvas()
        return self.shapes


# === EnclosingImageGenerator ===


class EnclosingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.enclose_level = GenerationConfig.enclosing_image_config.enclose_level

    def generate(self) -> ShapeGroup:
        self.canvas_radius_limit = min(
            GenerationConfig.canvas_height / 2, GenerationConfig.canvas_width / 2
        )
        self.generate_composite_image_nested(
            self.canvas_radius_limit, self.enclose_level
        )
        return self.shapes

    def generate_composite_image_nested(self, outer_radius, recur_depth):
        """generate a nested image, centered at 0,0, and within a square area of outer_size * outer_size"""
        if recur_depth <= 1:
            from image_generators import generate_shape_group

            core_shape_group = generate_shape_group()

            shrink_ratio = outer_radius / self.canvas_radius_limit
            core_shape_group.scale(shrink_ratio, origin=(0, 0))
            self.shapes.add_group(core_shape_group)
        else:
            outer_shape = SimpleShape(
                np.array([0.0, 0.0]),
                rotation=random.choice(list(img_params.Angle)),
                size=outer_radius,
            )
            self.shapes.add_shape(outer_shape)
            if outer_shape.shape == img_params.Shape.triangle:
                shrink_ratio = 0.4
            else:
                shrink_ratio = 0.6
            self.generate_composite_image_nested(
                outer_radius=outer_radius * shrink_ratio, recur_depth=recur_depth - 1
            )


# === RandomImageGenerator ===

class RandomImageGenerator(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.rotation=GenerationConfig.random_image_config.rotation
        self.element_num=GenerationConfig.random_image_config.element_num
    def generate(self) -> ShapeGroup:
        """generate a composite geometry entity by randomly placing simple shapes

        Args:
            position (numpy 2-d array): coordinate of the center of the radnom shape
            rotation (float): rotation angle in degree
        """
        for i in range(self.element_num):
            generation_config.step_into_config_scope("random_image_config")
            element = generate_shape_group()
            element.rotate(angle=random.choice(list(img_params.Angle)))
            element.scale(random.choice([1, 2, 4]) / self.element_num)
            # element.shift()
            random_shift = GenerationConfig.canvas_limit * random.random() * np.array(
                [random.uniform(-1, 1), random.uniform(-1, 1)]
            )
            element.shift(random_shift)
            self.shapes.add_group(element)
        self.shapes.fit_canvas()
        return self.shapes


# === RadialImageGenerator ===

class RadialImageGenerator(ImageGenerator):
    def __init__(self):
        super().__init__()
        self.rotation=GenerationConfig.radial_image_config.rotation
        self.element_num=GenerationConfig.radial_image_config.element_num
    def generate(self)->ShapeGroup:
        
        elements = ShapeGroup([[]])
        for i in range(self.element_num):
            generation_config.step_into_config_scope("radial_image_config")
            element = generate_shape_group()
            element.rotate(angle=360/self.element_num*(i))
            # element.shift()
            self.shapes.add_group(element)
        self.shapes.fit_canvas()
        return self.shapes


# === ParallelImageGenerator ===

class ParallelImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.position: Coordinate = (0, 0)
        self.rotation = GenerationConfig.parallel_image_config.rotation

        self.interval = GenerationConfig.parallel_image_config.interval
        self.element_num = GenerationConfig.parallel_image_config.element_num
        self.parallel_shape = GenerationConfig.parallel_image_config.parallel_shape
        self.groups = []  # all generated shape groups

    def generate_parallel_lines(self) -> List[LineString]:
        """Generate parallel lines based on configuration."""
        if self.parallel_shape == "horizontal":
            # Generate horizontal lines
            y_positions = np.linspace(
                -GenerationConfig.canvas_limit / 2,
                GenerationConfig.canvas_limit / 2,
                self.element_num
            )
            lines = []
            for y in y_positions:
                line = LineString([
                    (-GenerationConfig.canvas_limit / 2, y),
                    (GenerationConfig.canvas_limit / 2, y)
                ])
                lines.append(line)
            return lines
            
        elif self.parallel_shape == "vertical":
            # Generate vertical lines
            x_positions = np.linspace(
                -GenerationConfig.canvas_limit / 2,
                GenerationConfig.canvas_limit / 2,
                self.element_num
            )
            lines = []
            for x in x_positions:
                line = LineString([
                    (x, -GenerationConfig.canvas_limit / 2),
                    (x, GenerationConfig.canvas_limit / 2)
                ])
                lines.append(line)
            return lines
            
        elif self.parallel_shape == "diagonal":
            # Generate diagonal lines (45 degree angle)
            # Calculate the diagonal span needed
            canvas_diagonal = GenerationConfig.canvas_limit * np.sqrt(2)
            
            # Generate evenly spaced offsets
            offsets = np.linspace(
                -canvas_diagonal / 2,
                canvas_diagonal / 2,
                self.element_num
            )
            
            lines = []
            for offset in offsets:
                # For each offset, create a diagonal line
                # Line equation: y = x + offset
                # Find intersection with canvas boundaries
                x1 = -GenerationConfig.canvas_limit / 2
                y1 = x1 + offset
                x2 = GenerationConfig.canvas_limit / 2
                y2 = x2 + offset
                
                # Clip to canvas boundaries
                if y1 < -GenerationConfig.canvas_limit / 2:
                    y1 = -GenerationConfig.canvas_limit / 2
                    x1 = y1 - offset
                elif y1 > GenerationConfig.canvas_limit / 2:
                    y1 = GenerationConfig.canvas_limit / 2
                    x1 = y1 - offset
                    
                if y2 < -GenerationConfig.canvas_limit / 2:
                    y2 = -GenerationConfig.canvas_limit / 2
                    x2 = y2 - offset
                elif y2 > GenerationConfig.canvas_limit / 2:
                    y2 = GenerationConfig.canvas_limit / 2
                    x2 = y2 - offset
                
                line = LineString([(x1, y1), (x2, y2)])
                lines.append(line)
            return lines
            
        else:
            raise ValueError(f"Unknown parallel shape: {self.parallel_shape}")

    def place_shapes_on_lines(self, lines: List[LineString]):
        """Place shapes along the parallel lines."""
        for i, line in enumerate(lines):
            # Skip some lines randomly for visual variety
            if random.random() < 0.2:  # 20% chance to skip
                continue
                
            # Determine number of shapes on this line
            line_length = line.length
            num_shapes_on_line = max(1, int(line_length / (GenerationConfig.canvas_limit / 4)))
            
            # Generate positions along the line
            positions = []
            if num_shapes_on_line == 1:
                positions = [0.5]  # Middle of the line
            else:
                positions = np.linspace(0.1, 0.9, num_shapes_on_line)
            
            for pos in positions:
                # Get point at this position along the line
                point = line.interpolate(pos, normalized=True)
                
                # Generate a shape group at this position
                generation_config.step_into_config_scope("parallel_image_config")
                element_grp = generate_shape_group()
                
                # Scale based on interval
                scale_factor = (1 - self.interval) / (self.element_num * 0.5)
                element_grp.scale(scale_factor)
                
                # Move to position
                element_grp.shift(np.array([point.x, point.y]) - element_grp.center)
                
                # Add some random rotation for variety
                element_grp.rotate(angle=random.choice(list(img_params.Angle)))
                
                self.shapes.add_group(element_grp)
                self.groups.append(element_grp)

    def add_connecting_elements(self):
        """Add connecting elements between shapes if needed."""
        if len(self.groups) < 2:
            return
            
        # Randomly connect some adjacent shapes
        for i in range(len(self.groups) - 1):
            if random.random() < 0.3:  # 30% chance to connect
                shape1 = self.groups[i]
                shape2 = self.groups[i + 1]
                
                # Check if shapes are close enough
                dist = np.linalg.norm(shape1.center - shape2.center)
                if dist < GenerationConfig.canvas_limit / 3:
                    # Add connecting line
                    line = LineSegment.connect(
                        shape1.geometry(0),
                        shape2.geometry(0)
                    )
                    self.shapes.add_shape(line)

    def generate(self) -> ShapeGroup:
        """Generate a composite geometry entity with parallel arrangement.
        
        Returns:
            ShapeGroup: The generated shape group
        """
        # Generate the parallel lines
        lines = self.generate_parallel_lines()
        
        # Rotate all lines if needed
        if self.rotation != 0:
            from shapely.affinity import rotate
            lines = [rotate(line, self.rotation, origin=(0, 0)) for line in lines]
        
        # Place shapes on the lines
        self.place_shapes_on_lines(lines)
        
        # Add connecting elements
        self.add_connecting_elements()
        
        # Fit to canvas
        self.shapes.fit_canvas()
        
        return self.shapes


# === BorderImageGenerator ===

class BorderImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.position: Coordinate = (0, 0)
        self.interval = GenerationConfig.border_image_config.interval
        self.rotation = GenerationConfig.border_image_config.rotation
        self.border_shape = GenerationConfig.border_image_config.border_shape
        self.element_num = GenerationConfig.border_image_config.element_num
        self.border_points = []  # Positions for border elements

    def generate_border_points(self):
        """Generate points along the border shape."""
        if self.border_shape == "rectangle":
            # Generate points along a rectangle
            width = GenerationConfig.canvas_limit * 0.8
            height = GenerationConfig.canvas_limit * 0.6
            
            # Calculate perimeter and spacing
            perimeter = 2 * (width + height)
            spacing = perimeter / self.element_num
            
            points = []
            current_distance = 0
            
            # Top edge (left to right)
            for i in range(self.element_num):
                distance = i * spacing
                
                if distance < width:
                    # Top edge
                    x = -width/2 + distance
                    y = height/2
                elif distance < width + height:
                    # Right edge
                    x = width/2
                    y = height/2 - (distance - width)
                elif distance < 2*width + height:
                    # Bottom edge
                    x = width/2 - (distance - width - height)
                    y = -height/2
                else:
                    # Left edge
                    x = -width/2
                    y = -height/2 + (distance - 2*width - height)
                
                points.append((x, y))
            
            self.border_points = points
            
        elif self.border_shape == "circle":
            # Generate points along a circle
            radius = GenerationConfig.canvas_limit * 0.4
            angles = np.linspace(0, 2*np.pi, self.element_num, endpoint=False)
            
            self.border_points = [
                (radius * np.cos(angle), radius * np.sin(angle))
                for angle in angles
            ]
            
        elif self.border_shape == "triangle":
            # Generate points along a triangle
            # Define triangle vertices
            height = GenerationConfig.canvas_limit * 0.7
            base = GenerationConfig.canvas_limit * 0.8
            
            vertices = [
                (-base/2, -height/3),  # Bottom left
                (base/2, -height/3),   # Bottom right
                (0, 2*height/3)        # Top
            ]
            
            # Calculate perimeter
            sides = [
                np.linalg.norm(np.array(vertices[1]) - np.array(vertices[0])),
                np.linalg.norm(np.array(vertices[2]) - np.array(vertices[1])),
                np.linalg.norm(np.array(vertices[0]) - np.array(vertices[2]))
            ]
            perimeter = sum(sides)
            spacing = perimeter / self.element_num
            
            points = []
            for i in range(self.element_num):
                distance = i * spacing
                
                # Determine which side the point is on
                if distance < sides[0]:
                    # First side (bottom)
                    t = distance / sides[0]
                    point = (1-t) * np.array(vertices[0]) + t * np.array(vertices[1])
                elif distance < sides[0] + sides[1]:
                    # Second side (right)
                    t = (distance - sides[0]) / sides[1]
                    point = (1-t) * np.array(vertices[1]) + t * np.array(vertices[2])
                else:
                    # Third side (left)
                    t = (distance - sides[0] - sides[1]) / sides[2]
                    point = (1-t) * np.array(vertices[2]) + t * np.array(vertices[0])
                
                points.append(tuple(point))
            
            self.border_points = points
        
        else:
            raise ValueError(f"Unknown border shape: {self.border_shape}")

    def generate_shapes_on_border(self):
        """Place shapes at border points."""
        prev_element = None
        
        for i, point in enumerate(self.border_points):
            # Generate shape group
            generation_config.step_into_config_scope("border_image_config")
            element_grp = generate_shape_group()
            
            # Scale based on element number and interval
            scale_factor = 1 / (self.element_num * 0.3)
            scale_factor *= (1 - self.interval)
            element_grp.scale(scale_factor)
            
            # Move to border position
            element_grp.shift(np.array(point) - element_grp.center)
            
            # Rotate shape
            # For circular borders, orient shapes outward
            if self.border_shape == "circle":
                angle = np.arctan2(point[1], point[0]) * 180 / np.pi
                element_grp.rotate(angle=angle)
            else:
                element_grp.rotate(angle=random.choice(list(img_params.Angle)))
            
            # Adjust size to maintain interval with previous element
            if prev_element is not None and i > 0:
                # Check if current element overlaps too much with previous
                curr_geom = element_grp.geometry(0)
                prev_geom = prev_element.geometry(0)
                
                if isinstance(curr_geom, shapely.geometry.base.BaseGeometry) and \
                   isinstance(prev_geom, shapely.geometry.base.BaseGeometry):
                    # Calculate distance between geometries
                    distance = curr_geom.distance(prev_geom)
                    
                    # If too close, scale down
                    if distance < self.interval * GenerationConfig.canvas_limit * 0.05:
                        scale_adjust = 0.8
                        element_grp.scale(scale_adjust)
            
            prev_element = element_grp
            self.shapes.add_group(element_grp)

    def add_connecting_lines(self):
        """Add lines connecting border elements."""
        if self.element_num < 2:
            return
            
        # Connect consecutive border elements
        for i in range(self.element_num):
            next_i = (i + 1) % self.element_num
            
            # Get the shapes at these positions
            if i < len(self.shapes.shape_groups) and next_i < len(self.shapes.shape_groups):
                shape1 = self.shapes.shape_groups[i]
                shape2 = self.shapes.shape_groups[next_i]
                
                # Add connecting line
                try:
                    line = LineSegment.connect(
                        shape1.geometry(0),
                        shape2.geometry(0)
                    )
                    self.shapes.add_shape(line)
                except:
                    # If connection fails, skip
                    pass

    def generate(self) -> ShapeGroup:
        """Generate a composite geometry entity with border arrangement.
        
        Returns:
            ShapeGroup: The generated shape group
        """
        # Generate border points
        self.generate_border_points()
        
        # Apply rotation to all points if needed
        if self.rotation != 0:
            angle_rad = self.rotation * np.pi / 180
            rotation_matrix = np.array([
                [np.cos(angle_rad), -np.sin(angle_rad)],
                [np.sin(angle_rad), np.cos(angle_rad)]
            ])
            
            self.border_points = [
                tuple(rotation_matrix @ np.array(point))
                for point in self.border_points
            ]
        
        # Place shapes on border
        self.generate_shapes_on_border()
        
        # Add connecting lines if configured
        if hasattr(GenerationConfig.border_image_config, 'add_connections') and \
           GenerationConfig.border_image_config.add_connections:
            self.add_connecting_lines()
        
        # Fit to canvas
        self.shapes.fit_canvas()
        
        return self.shapes


# === 辅助函数 ===

def get_image_generator(composition_type: str) -> ImageGenerator:
    """根据组合类型返回相应的图像生成器实例"""
    if composition_type == "simple":
        return SimpleImageGenerator()
    elif composition_type == "chaining":
        return ChainingImageGenerator()
    elif composition_type == "enclosing":
        return EnclosingImageGenerator()
    elif composition_type == "random":
        return RandomImageGenerator()
    elif composition_type == "border":
        return BorderImageGenerator()
    elif composition_type == "parallel":
        return ParallelImageGenerator()
    elif composition_type == "radial":
        return RadialImageGenerator()
    else:
        raise ValueError(f"Invalid composition type: {composition_type}")
    
def get_config_name(generator: ImageGenerator) -> str:
    """根据生成器实例返回相应的配置名称"""
    d = {
        "SimpleImageGenerator": "simple_image_config",
        "ChainingImageGenerator": "chaining_image_config",
        "EnclosingImageGenerator": "enclosing_image_config",
        "RandomImageGenerator": "random_image_config",
        "BorderImageGenerator": "border_image_config",
        "ParallelImageGenerator": "parallel_image_config",
        "RadialImageGenerator": "radial_image_config",
    }
    return d[generator.__class__.__name__]


# @step_out_config_scope
def generate_shape_group() -> ShapeGroup:
    """生成一个形状组"""
    composition_type = random.choices(
        list(GenerationConfig.composition_type.keys()),
        list(GenerationConfig.composition_type.values()),
    )[0]
    generator = get_image_generator(composition_type)
    cfg_name = get_config_name(generator)
    generation_config.step_into_config_scope(cfg_name)
    elements: ShapeGroup = generator.generate()
    return elements


__all__ = [
    "ImageGenerator",
    "SimpleImageGenerator",
    "ChainingImageGenerator", 
    "EnclosingImageGenerator", 
    "ParallelImageGenerator", 
    "RandomImageGenerator", 
    "BorderImageGenerator",
    "RadialImageGenerator",
    "get_image_generator",
    "generate_shape_group"
] 
