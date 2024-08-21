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


def combine_images(composition_type:img_params.Composition):
    """combine images of each sub-panel


    """    
    layout = random.choice(list(img_params.Layout))
    panel_num = int(layout.value)
    instructions = []
    # for each panel, draw simple shapes
    for i in range(panel_num):
        pos = compute_panel_position(layout, i)
        rot = random.choice(list(img_params.Rotation)).value * random.randint(0, 23)
        if composition_type == img_params.Composition.SIMPLE:
            img = generate_simple_shape(position=pos,rotation=rot)
            inst = convert_tikz_instruction(img)
        elif composition_type==img_params.Composition.CHAIN:
            img = generate_composite_image_chaining(position=pos,rotation=rot,size=img_params.Size.XS)
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


def generate_simple_shape(
    position: np.ndarray,
    rotation: float,
    size: Optional[int] = None,
    shape: Optional[img_params.Shape] = None,
    color: Optional[img_params.Color] = None,
    pattern: Optional[img_params.Pattern] = None,
) -> SimpleShape:
    """
    arguments:
    position (numpy 2-d row vector): define the position of the center,
    rotation (int or float): the counter-clockwise rotation in degree

    returns
    str: the tikz instruction to draw a random simple geometry object.
    """
    generated_shape = SimpleShape()
    generated_shape.position = position
    generated_shape.rotation = rotation
    generated_shape.shape = shape if shape is not None else random.choice(list(img_params.Shape))
    generated_shape.size = size if size is not None else random.choice(list(img_params.Size))
    generated_shape.color = color if color is not None else random.choice(list(img_params.Color))
    generated_shape.pattern = pattern if pattern is not None else random.choice(list(img_params.Pattern))

    return generated_shape


def generate_composite_image_chaining(position,rotation,element_num = 4, chain_direction:Optional[np.ndarray] = None,size:Optional[img_params.Size] = None):
    """generate a composite geometry entity by chaining simple shapes

    Args:
        position (numpy 2-d array): coordinate of the center
        rotation (float): rotation in degree
    """    

    # composite the image first, then shift to the center pos

    shapes = [0]*element_num
    new_size = random.choice(list(img_params.Size)) if size is None else size
    for i in range(element_num):
        new_element = generate_simple_shape(position,rotation,size=new_size)
        shapes[i] = new_element
        attach_position = new_element.get_attach_point()
        # new_size = random.choice(list(img_params.Size))
        new_size = random.choice(list(img_params.Size)) if size is None else size
        if chain_direction is not None:
            unit_direction = chain_direction / np.linalg.norm(chain_direction)
            position = attach_position + unit_direction*new_size.value
            continue

        if new_element.shape==img_params.Shape.LINE:
            rand_rad = random.random() * 2*math.pi
            position = attach_position + new_size.value * np.array([math.cos(rand_rad),math.sin(rand_rad)])
            continue
        
        unit_vec_center_to_touching = (attach_position - new_element.position)
        unit_vec_center_to_touching /= np.linalg.norm(unit_vec_center_to_touching)
        position = attach_position+unit_vec_center_to_touching * new_size.value
    # print(shapes)
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
