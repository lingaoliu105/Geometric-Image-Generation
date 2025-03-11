
from common_types import *
from entities.closed_shape import ClosedShape
from entities.line_segment import LineSegment
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from shape_group import ShapeGroup
from util import *
from shapely import LineString, Point

class ChainingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.position: Coordinate = (0, 0)
        # TODO: combine the chain linesegments into one entity for json labelling

        # TODO: add default value when some configs are not given by user
        self.draw_chain = generation_config.GenerationConfig.chaining_image_config[
            "draw_chain"
        ]
        self.chain_shape = generation_config.GenerationConfig.chaining_image_config[
            "chain_shape"
        ]
        self.element_num = GenerationConfig.chaining_image_config["element_num"]
        self.interval = GenerationConfig.chaining_image_config["interval"]
        self.chain = []  # initial positions of each element
        self.rotation = GenerationConfig.chaining_image_config["rotation"]
        self.chain_level = GenerationConfig.chaining_image_config["chain_level"]
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

            sub_generator = self.choose_sub_generator()
            element_grp = sub_generator.generate()
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
