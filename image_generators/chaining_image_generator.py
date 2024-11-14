from math import ceil

from shapely import LineString, Point, Polygon, within
from common_types import *
from entities.entity import ClosedShape, VisibleShape
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from entities.touching_point import TouchingPoint
from image_generators.image_generator import ImageGenerator
from panel import Panel
from util import *


class ChainingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        self.position: Coordinate = (0, 0)
        self.draw_chain = False
        self.chain_shape = "line"
        self.shapes = []
        self.element_num = ceil(generate_beta_random_with_mode(0.2, 2) * 19) 
        self.interval = 0.0
        self.chain = []

    def generate_chain(self):
        assert self.element_num >= 2 and self.element_num <= 20
        # composite the image first, then shift to the center pos
        if self.chain_shape == "bezier":
            curve_function = lambda: generate_bezier_curve_single_param(1)
        elif self.chain_shape == "circle":
            curve_function = lambda: generate_circle_curve(random.randrange(4, 8))
        elif self.chain_shape == "line":
            curve_function = lambda: get_points_on_line((-5.0, 5.0), (5.0, -5.0))
        else:
            print("curve type not assigned")
            raise
        curve_point_set = curve_function()

        def get_chain():
            step_length = len(curve_point_set) // self.element_num
            chain = [
                curve_point_set[step_length * index]
                for index in range(self.element_num)
            ]  # the set of all centers of the element shapes
            return chain

        self.chain = get_chain()
        if self.draw_chain:
            self.shapes += [
                LineSegment(
                    curve_point_set[i], curve_point_set[i + 1], img_params.Color.black
                )
                for i in range(len(curve_point_set) - 2)
            ]

    def generate_shapes_on_chain(self):
        for i in range(self.element_num):
            # skip if current center is already covered by the previous shape
            if len(self.shapes) > 0 and shapely.Point(self.chain[i]).within(
                self.shapes[-1].expand_fixed(self.interval).base_geometry
            ):
                continue

            use_closed_shape = random.random() < 0.6
            if use_closed_shape:
                element_rotation = get_random_rotation()
                if i == 0:
                    element_size = get_point_distance(self.chain[0], self.chain[1]) * (
                        random.random() / 2 + 0.25
                    )
                else:
                    element_size = (
                        get_point_distance(self.chain[i], self.shapes[-1].position) * 2
                    )
                element = SimpleShape(
                    position=self.chain[i],
                    rotation=element_rotation,
                    size=element_size,
                )  
                if i != 0:
                    element.search_size_by_interval(self.shapes[-1], self.interval)
            else:
                if i == 0:
                    # for the line segment as the head, randomly choose endpoints
                    element = LineSegment.within_distance(self.chain[i], self.interval)
                else:
                    next_endpoint = self.chain[i]
                    def choose_endpoint_around_shape():
                        def sample_geometry_boundary(geometry, num_points=30):
                            if isinstance(geometry, Polygon):
                                # 获取多边形的外环
                                exterior_coords = geometry.exterior.coords
                                if (
                                    len(exterior_coords) >= num_points
                                ):  # most likely a circle
                                    return exterior_coords
                                geometry = LineString(exterior_coords)

                            # 根据周长进行等距采样
                            sampled_points = []
                            for i in np.linspace(0, geometry.length, num_points):
                                sampled_points.append(geometry.interpolate(i).coords[0])
                            return sampled_points

                        prev = self.shapes[-1]
                        expanded_prev: VisibleShape = prev if isinstance(prev,LineSegment) and prev.is_expanded else prev.expand_fixed(self.interval)
                        # pick a point on the expanded shape, which faces the next endpoint
                        bound_points: list = sample_geometry_boundary(
                            expanded_prev.base_geometry
                        )
                        filtered_bound_points = list(
                            filter(
                                lambda point: not LineString(
                                    [point, next_endpoint]
                                ).intersects(expanded_prev.base_geometry)
                                or LineString([point, next_endpoint]).touches(
                                    expanded_prev.base_geometry
                                ),
                                bound_points,
                            )
                        )
                        if len(filtered_bound_points) == 0: # don't know why no point passed the filter. if so, simply choose the point directly facing the next endpoint
                            return LineString([next_endpoint,expanded_prev.position]).intersection().coords[0]
                        return random.choice(filtered_bound_points)

                    start_point = choose_endpoint_around_shape()
                    element = LineSegment(start_point, next_endpoint)
                    element.scale_with_pivot(random.uniform(1, 2), start_point)
                    element.expand_fixed(self.interval)

                # if i != 0:
                #     element.adjust_by_interval(
                #         self.shapes[-1], self.interval, prior_method="rotate"
                #     )

            self.shapes.append(element)

    def generate(self) -> Panel:
        """generate a composite geometry entity by chaining simple shapes

        Args:
            position (numpy 2-d array): coordinate of the center of the chained shape
            rotation (float): rotation of the overall composite chained shapes in degree
        """
        self.generate_chain()
        self.generate_shapes_on_chain()

        touching_points = []
        for i, shape in enumerate(self.shapes):
            shape.shift(self.position)
            if i > 0:
                touching_points.append(TouchingPoint(self.shapes[i - 1], shape))
        return Panel(
            top_left=self.panel_top_left,
            bottom_right=self.panel_bottom_right,
            shapes=self.shapes,
            joints=touching_points,
        )