
from common_types import *
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
        self.sub_generators = {SimpleImageGenerator:1.0} # default value
        self.rotation = GenerationConfig.chaining_image_config["rotation"]
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
            if len(self.shapes[0]) > 0 and shapely.Point(self.chain[i]).within(
                self.shapes[0][-1].expand_fixed(max(self.interval,0.0)).base_geometry
            ):
                continue
            sub_generator = self.choose_sub_generator()
            element_grp = sub_generator.generate()
            element_grp.scale(1/self.element_num)
            element_grp.shift(self.chain[i]-element_grp.center)
            element_grp.rotate(angle=random.choice(list(img_params.Angle)))

            if i != 0 and element_grp.size()==1 and isinstance(element_grp[0][0],SimpleShape):
                prev_shape = self.shapes[0][-1]
                simple_shape_element = element_grp[0][0]
                simple_shape_element.scale(2*get_point_distance(prev_shape.center, self.chain[i]) / simple_shape_element.size) # expand new shape to make sure it overlaps prev to guarantee size search result
                simple_shape_element.search_size_by_interval(prev_shape, self.interval)

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
            top_layer = self.shapes.layer_num-1
            for seg in chain_segments:
                self.shapes.add_shape_on_layer(seg,top_layer)
        return self.shapes
