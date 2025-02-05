
from re import sub
from common_types import *
from entities.closed_shape import ClosedShape
from entities.complex_shape import ComplexShape
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from generation_config import GenerationConfig
from image_generators.image_generator import ImageGenerator
from image_generators.simple_image_generator import SimpleImageGenerator
from shape_group import ShapeGroup
from util import *


class ChainingImageGenerator(ImageGenerator):
    def __init__(self) -> None:
        super().__init__()
        self.position: Coordinate = (0, 0)
        # TODO: combine the chain linesegments into one entity for json labelling
        
        # TODO: add default value when some configs are not given by user
        self.draw_chain = generation_config.GenerationConfig.chaining_image_config['draw_chain']
        self.chain_shape = generation_config.GenerationConfig.chaining_image_config['chain_shape']
        self.element_num = GenerationConfig.chaining_image_config["element_num"]
        self.interval = GenerationConfig.chaining_image_config['interval']
        self.chain = [] # initial positions of each element
        self.rotation = GenerationConfig.chaining_image_config["rotation"]
        self.chain_level = GenerationConfig.chaining_image_config["chain_level"]

    def generate_chain(self):
        assert self.element_num >= 2 and self.element_num <= 20
        # composite the image first, then shift to the center pos
        if self.chain_shape == "bezier":
            curve_function = lambda: generate_random_bezier_curve()
        elif self.chain_shape == "circle":
            curve_function = lambda: generate_circle_curve(random.randrange(4, 8))
        elif self.chain_shape == "line":
            curve_function = lambda: get_points_on_line((-5.0, 0.0), (5.0, 0.0))
        else:
            print("curve type not assigned")
            raise
        self.curve_point_set = curve_function()
        self.curve_point_set = [rotate_point(pt,(0,0),self.rotation) for pt in self.curve_point_set]

        def get_chain():
            step_length = max(1,len(self.curve_point_set) // (self.element_num-1))
            chain = [
                self.curve_point_set[min(step_length * index, len(self.curve_point_set) - 1)]
                for index in range(self.element_num)
            ] # the set of all centers of the element shapes
            return chain

        self.chain = get_chain()


    def generate_shapes_on_chain(self):
        for i in range(self.element_num):
            # skip if current center is already covered by the previous shape
            if shapely.Point(self.chain[i]).within(
                self.shapes.geometry(0).buffer(self.interval)
            ):
                continue
            sub_generator = self.choose_sub_generator()
            element_grp = sub_generator.generate()
            element_grp.shift(self.chain[i]-element_grp.center)
            element_grp.scale(1/self.element_num)
            element_grp.scale(1-self.interval / GenerationConfig.canvas_height / 2)
            element_grp.rotate(angle=random.choice(list(img_params.Angle)))

            if i != 0 and any([isinstance(shape,ClosedShape) for shape in element_grp[0]]):
                while not (element_grp.geometry(0).overlaps(prev_elements.geometry(0)) or element_grp.geometry(0).contains(prev_elements.geometry(0))):
                    element_grp.scale(2) # expand new shape to make sure it overlaps prev to guarantee size search result
                element_grp.search_size_by_interval(prev_elements, self.interval)
            prev_elements = element_grp
            self.shapes.add_group(element_grp)

    def generate(self) -> ShapeGroup:
        """generate a composite geometry entity by chaining simple shapes

        Args:
            position (numpy 2-d array): coordinate of the center of the chained shape
            rotation (float): rotation of the overall composite chained shapes in degree
        """
        self.generate_chain()
        self.generate_shapes_on_chain()
        if self.draw_chain:
            chain_segments = [
                LineSegment(
                    self.curve_point_set[i], self.curve_point_set[i + 1]
                )
                for i in range(len(self.curve_point_set) - 2)
                # for i in range(0,len(self.curve_point_set) - 2,2)
            ]
            if self.chain_level=="bottom":
                self.shapes.lift_up_layer()
                for seg in chain_segments:
                    self.shapes.add_shape_on_layer(seg,0)
            elif self.chain_level=="top":
                top_layer = self.shapes.layer_num-1
                for seg in chain_segments:
                    self.shapes.add_shape_on_layer(seg,top_layer)
            else:
                raise ValueError()
        self.shapes.fit_canvas()
        self.shapes.show()
        return self.shapes
