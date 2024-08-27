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

generate_num = 10


def combine_images(composition_type: img_params.Composition):
    """combine images of each sub-panel"""
    layout = random.choice(list(img_params.Layout))
    panel_num = int(layout.value)
    instructions = []
    # for each panel, draw simple shapes
    for i in range(panel_num):
        pos = compute_panel_position(layout, i)
        rot = get_random_rotation()
        if composition_type == img_params.Composition.SIMPLE:
            img = SimpleShape(position=pos, rotation=rot)
            inst = convert_tikz_instruction(img)
        elif composition_type == img_params.Composition.CHAIN:
            img = generate_composite_image_chaining(position=pos, rotation=rot)
            inst = convert_tikz_instructions(img)
        instructions.append(inst)
    return instructions


def compute_panel_position(layout, index):
    """
    arguments:
    layout(Layout): the layout of the image
    index(int): the index of the panel to compute, starting from 0

    output:
    ndarray[(float,float)]: the x-coordinate and y-coordinate of the center of the panel (assume the whole image is 20cm x 20cm)
    """
    lookup_table = {
        img_params.Layout.SINGLE: [(0, 0)],
        img_params.Layout.LR: [(-5, 0), (5, 0)],
        img_params.Layout.UD: [(0, 5), (0, -5)],
        img_params.Layout.QUADRANT: [(-5, 5), (5, 5), (-5, -5), (5, -5)],
        img_params.Layout.FEFT: [(-1.6, 1.6), (1.6, 1.6), (-1.6, -1.6), (1.6, -1.6)],
        img_params.Layout.GRID: [
            (-6.67, 6.67),
            (0, 6.67),
            (6.67, 6.67),
            (-6.67, 0),
            (0, 0),
            (6.67, 0),
            (-6.67, -6.67),
            (0, -6.67),
            (6.67, -6.67),
        ],
    }
    return np.array(lookup_table[layout][index])


def generate_composite_image_chaining(position, rotation, element_num=10):
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
        print(element_size)
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
    tikz_instructions = combine_images(composition_type=img_params.Composition.CHAIN)
    context = {"tikz_instructions": tikz_instructions}
    output = template.render(context)

    latex_filename = f"new{n}.tex"
    with open(f"./output_tex/{latex_filename}", "w", encoding="utf-8") as f:
        f.write(output)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1]:
        generate_num = int(sys.argv[1])
    for i in range(generate_num):
        main(i)
