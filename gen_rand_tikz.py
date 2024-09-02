import json
import random
from typing import Optional
from jinja2 import Environment, FileSystemLoader

from convert_tikz import *
import img_params
import sys
from SimpleShape import SimpleShape
import numpy as np
import shapely
from util import *
import math

generate_num = 1


def combine_panel_images(composition_type: img_params.Composition, layout:Optional[img_params.Layout] = None) -> list[SimpleShape]:
    """combine images of each sub-panel"""
    layout = random.choice(list(img_params.Layout)) if layout is None else layout
    panel_num = int(layout.value) if composition_type != img_params.Composition.NESTING else 1
    images = []
    # for each panel, draw simple shapes
    for i in range(panel_num):
        pos = compute_panel_position(layout, i)
        rot = get_random_rotation()
        if composition_type == img_params.Composition.SIMPLE:
            img = [SimpleShape(position=pos, rotation=rot)]
        elif composition_type == img_params.Composition.CHAIN:
            img = generate_composite_image_chaining(position=pos, rotation=rot)
        elif composition_type == img_params.Composition.NESTING:
            img = generate_composite_image_nested()
        images+=img
    return images


def compute_panel_position(layout, index):
    """
    arguments:
    layout(Layout): the layout of the image
    index(int): the index of the panel to compute, starting from 0

    output:
    ndarray[(float,float)]: the x-coordinate and y-coordinate of the center of the panel (assume the whole image is 20cm x 20cm)
    """
    lookup_table = {
        img_params.Layout.SINGLE: [(0.0, 0.0)],
        img_params.Layout.LR: [(-5.0, 0.0), (5.0, 0.0)],
        img_params.Layout.UD: [(0.0, 5.0), (0.0, -5.0)],
        img_params.Layout.QUADRANT: [(-5.0, 5.0), (5.0, 5.0), (-5.0, -5.0), (5.0, -5.0)],
        img_params.Layout.FEFT: [(-1.6, 1.6), (1.6, 1.6), (-1.6, -1.6), (1.6, -1.6)],
        img_params.Layout.GRID: [
            (-6.67, 6.67),
            (0.0, 6.67),
            (6.67, 6.67),
            (-6.67, 0),
            (0.0, 0),
            (6.67, 0),
            (-6.67, -6.67),
            (0.0, -6.67),
            (6.67, -6.67),
        ],
    }
    return np.array(lookup_table[layout][index])

def generate_composite_image_nested(outer_size = 20.0,recur_depth = 2)->list[SimpleShape]:
    """generate a nested image, centered at 0,0, and within a square area of outer_size * outer_size

    Args:
        outer_size (int, optional): the length of edge of the square frame. Defaults to 20.
    """    
    if recur_depth==0:
        panel_images = combine_panel_images(img_params.Composition.SIMPLE)
        for image in panel_images:
            shrink_ratio = outer_size/20
            image.shift(-shrink_ratio*image.position)
            image.set_size(image.size * shrink_ratio)
        return panel_images
    else:
        rotation = 0 # TODO: may change to random rotation in the future
        shape_list = []
        outer_shape = SimpleShape(np.array([0.0,0.0]),rotation,size=outer_size/2.0)
        shape_list.append(outer_shape)
        if outer_shape.shape == img_params.Shape.TRIANGLE_EQ:
            shrink_ratio = 0.6
        else:
            shrink_ratio = 0.8
        shape_list += generate_composite_image_nested(outer_size=outer_size*shrink_ratio,recur_depth=recur_depth-1)
        return shape_list
    
def generate_composite_image_chaining(position, rotation, element_num=10) -> list[SimpleShape]:
    """generate a composite geometry entity by chaining simple shapes

    Args:
        position (numpy 2-d array): coordinate of the center of the chained shape
        rotation (float): rotation of the overall composite chained shapes in degree
    """

    # composite the image first, then shift to the center pos
    curve_point_set = generate_bezier_curve_single_param(1)
    chain = [
        curve_point_set[element_num * index]
        for index in range(len(curve_point_set) // element_num)
    ]  # the set of all centers of the element shapes

    shapes = []
    for i in range(element_num):
        if len(shapes) > 0 and shapely.Point(chain[i]).within(shapes[-1].base_geometry):
            continue
        element_rotation = get_random_rotation()
        if i == 0:
            element_size = get_point_distance(chain[0], chain[1]) * random.random()
        else:
            element_size = get_point_distance(chain[i], chain[i - 1]) * 2
        element = SimpleShape(
            position=chain[i],
            rotation=element_rotation,
            size=element_size,
            excluded_shapes_set=set([img_params.Shape.LINE]),
        )  # exclude lines for now
        shapes.append(element)
        if i != 0:
            element.search_touching_size(shapes[i - 1])
    for shape in shapes:
        shape.shift(position)
    return shapes


def main(n):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("tikz_template.jinja")
    shapes = combine_panel_images(composition_type=img_params.Composition.NESTING,layout=img_params.Layout.SINGLE)
    tikz_instructions = convert_tikz_instructions(shapes)
    context = {"tikz_instructions": tikz_instructions}
    output = template.render(context)

    
    latex_filename = f"new{n}.tex"
    with open(f"./output_tex/{latex_filename}", "w", encoding="utf-8") as f:
        f.write(output)
        
    json_filename = f"new{n}.json"
    with open(f"./output_json/{json_filename}", "w", encoding="utf-8") as f:
        json.dump([item.to_dict() for item in shapes],f,indent=4)
        

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1]:
        generate_num = int(sys.argv[1])
    for i in range(generate_num):
        main(i)
