from math import ceil
from common_types import *
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from entities.touching_point import TouchingPoint
from image_generators.image_generator import ImageGenerator
from panel import Panel
from util import *

class ChainingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        self.position:Coordinate = (0,0)
        self.draw_chain = True
        self.chain_shape = "line"
        self.shapes_list = []
        self.element_num = ceil(generate_beta_random_with_mode(0.4, 2) * 19) + 1
        self.interval = 0.0

    def generate(self) -> Panel:
        """generate a composite geometry entity by chaining simple shapes

        Args:
            position (numpy 2-d array): coordinate of the center of the chained shape
            rotation (float): rotation of the overall composite chained shapes in degree
        """

        assert self.element_num >= 2 and self.element_num <= 20
        # composite the image first, then shift to the center pos
        if self.chain_shape == "bezier":
            curve_function = lambda: generate_bezier_curve_single_param(1)
        elif self.chain_shape == "circle":
            curve_function = lambda: generate_circle_curve(random.randrange(4, 8))
        elif self.chain_shape =="line":
            curve_function = lambda:get_points_on_line((-5.0,5.0),(5.0,-5.0))
        else:
            print("curve type not assigned")
            raise
        curve_point_set = curve_function()
        def get_chain():
            step_length = len(curve_point_set) // self.element_num
            chain = [
                curve_point_set[step_length * index] for index in range(self.element_num)
            ]  # the set of all centers of the element shapes
            return chain

        chain = get_chain()
        chain_shapes = [LineSegment(curve_point_set[i],curve_point_set[i+1],img_params.Color.black) for i in range(len(curve_point_set)-2)]

        shapes = []  # stack of shapes

        flag = True
        while flag:

            try:
                for i in range(self.element_num):

                    # skip if current center is already covered by the previous shape
                    if len(shapes) > 0 and shapely.Point(chain[i]).within(
                        shapes[-1].base_geometry
                    ):
                        continue

                    element_rotation = get_random_rotation()
                    if i == 0:
                        element_size = get_point_distance(chain[0], chain[1]) * (
                            random.random() / 2 + 0.25
                        )
                    else:
                        element_size = get_point_distance(chain[i], shapes[-1].position) * 2

                    a = random.random()
                    if a<0.6:
                        element = SimpleShape(
                            position=chain[i],
                            rotation=element_rotation,
                            size=element_size,
                            excluded_shapes_set=set([img_params.Shape.linesegment]),
                        )  # exclude lines for now
                        if i != 0:
                            element.search_size_by_interval(shapes[-1],self.interval)
                    else:
                        offset = np.array([1,0])
                        element = LineSegment(chain[i] + offset,chain[i] - offset)
                        if i!=0:
                            element.adjust_by_interval(shapes[-1],self.interval,prior_method="rotate")

                    shapes.append(element)
                flag = False
            except AssertionError:
                shapes.clear()

        touching_points = []
        for i, shape in enumerate(shapes):
            shape.shift(self.position)
            if i > 0:
                touching_points.append(TouchingPoint(shapes[i - 1], shape))
        return Panel(
            top_left=self.panel_top_left,
            bottom_right=self.panel_bottom_right,
            shapes=shapes+chain_shapes if self.draw_chain else shapes,
            joints=touching_points,
        )
