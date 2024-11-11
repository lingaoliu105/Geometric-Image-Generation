import json
from math import ceil
import math
import random
from typing import List, Literal
from jinja2 import Environment, FileSystemLoader

import generation_config
from entities.line_segment import LineSegment
from panel import Panel
from entities.touching_point import TouchingPoint
from tikz_converters import *
import img_params
import sys
from entities.simple_shape import SimpleShape
import numpy as np
import shapely
from util import *
from image_generators import ChainingImageGenerator


def generate_panels(
    composition_type: img_params.Composition, layout: tuple[int, int]
) -> list[Panel]:
    """combine images of each sub-panel"""
    row_num = layout[0]
    col_num = layout[1]
    panel_num = (
        row_num * col_num if composition_type != img_params.Composition.NESTING else 1
    )
    panels = []
    # for each panel, draw simple shapes
    for i in range(panel_num):
        center, top_left, bottom_right = compute_panel_position(layout, i)
        rot = get_random_rotation()
        if composition_type == img_params.Composition.SIMPLE:
            panel = Panel(
                top_left=top_left,
                bottom_right=bottom_right,
                shapes=[SimpleShape(position=center, rotation=rot)],
                joints=[],
            )
        elif composition_type == img_params.Composition.CHAIN:
            # random number of base elements, selected by beta distribution, ranged from 0 to 20
            generator = ChainingImageGenerator()
            generator.panel_top_left=top_left
            generator.panel_bottom_right=bottom_right
            panel = generator.generate()
        elif composition_type == img_params.Composition.NESTING:
            panel = generate_composite_image_nested()
        panels.append(panel)
    return panels


def compute_panel_position(layout: tuple[int, int], index: int):
    convert = lambda x: [
        x[0] - generation_config.GenerationConfig.canvas_width / 2.0,
        generation_config.GenerationConfig.canvas_height / 2.0 - x[1],
    ]
    row_num = layout[0]
    col_num = layout[1]
    panel_row = index // col_num
    panel_col = index % col_num
    row_height = generation_config.GenerationConfig.canvas_height * 1.0 / row_num
    col_width = generation_config.GenerationConfig.canvas_width * 1.0 / col_num

    center_coord = convert(
        [col_width / 2.0 * (panel_col * 2 + 1), row_height / 2.0 * (panel_row * 2 + 1)]
    )
    top_left_coord = convert([panel_col * col_width, panel_row * row_height])
    bottom_right_coord = convert(
        [(panel_col + 1) * col_width, (panel_row + 1) * row_height]
    )
    return center_coord, top_left_coord, bottom_right_coord


def generate_composite_image_nested(
    outer_size=20.0, recur_depth=2
) -> list[SimpleShape]:
    """generate a nested image, centered at 0,0, and within a square area of outer_size * outer_size

    Args:
        outer_size (int, optional): the length of edge of the square frame. Defaults to 20.
    """
    if recur_depth == 0:
        panel_images = generate_panels(img_params.Composition.SIMPLE)
        for image in panel_images:
            shrink_ratio = outer_size / 20
            image.shift(-shrink_ratio * image.position)
            image.set_size(image.size * shrink_ratio)
        return panel_images
    else:
        rotation = 0  # TODO: may change to random rotation in the future
        shape_list = []
        outer_shape = SimpleShape(np.array([0.0, 0.0]), rotation, size=outer_size / 2.0)
        shape_list.append(outer_shape)
        if outer_shape.shape == img_params.Shape.triangle:
            shrink_ratio = 0.6
        else:
            shrink_ratio = 0.8
        shape_list += generate_composite_image_nested(
            outer_size=outer_size * shrink_ratio, recur_depth=recur_depth - 1
        )
        return shape_list

def generate_consecutive_line_segments(position, num_lines:int = 8, mode:Literal["orthogonal","random"] = "random") -> List[LineSegment]:
    init = np.array([0.0,0.0])
    output_line_segments = []
    left_bound, right_bound,upper_bound, lower_bound = init[0],init[0],init[1],init[1]
    direction = -1
    for _ in range (num_lines):
        if mode=="orthogonal":
            direction = random.choice([x for x in [0,90,180,270] if x!=direction])
        elif mode=="random":
            direction = random.uniform(0,360)
            
        length = random.uniform(0,5)
        end = init + length * np.array([math.cos(math.radians(direction)),math.sin(math.radians(direction))])
        if end[0]<left_bound:
            left_bound = end[0]
        if end[0]>right_bound:
            right_bound = end[0]
        if end[1]<lower_bound:
            lower_bound = end[1]
        if end[1]>upper_bound:
            upper_bound = end[1]
        comp_key = lambda p: (p[0], -p[1])
        print(init)
        print(end)
        line_seg = LineSegment(pt1 = min(init,end,key=comp_key),pt2 = max(init,end,key=comp_key))
        output_line_segments.append(line_seg)
        init = end
        
    actual_center = np.array([(left_bound+right_bound)/2,(upper_bound+lower_bound)/2])
    offset = position - actual_center
    for l in output_line_segments:
        l.shift(offset)
    return output_line_segments

def generate_comb_line_segments(position,num_teeth = 8) -> List[LineSegment]:
    mid_string = LineSegment([-5,0],[5,0])
    output_line_segs = []
    fractions = sorted([random.random() for _ in range(num_teeth)])
    intersection_points = [mid_string.find_fraction_point(f) for f in fractions]
    for pt in intersection_points:
        other_pt = get_rand_point()
        new_ls = LineSegment(pt,other_pt,color=img_params.Color.black)
        output_line_segs.append(new_ls)
    # left_bound,right_bound,lower_bound,upper_bound = 
    return output_line_segs
    

def main(n):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("tikz_template.jinja")
    panels = generate_panels(
        composition_type=img_params.Composition.CHAIN, layout=(1, 1)
    )
    tikz_instructions = convert_panels(panels)
    # tikz_instructions = [line.to_tikz() for line in generate_consecutive_line_segments(position=(0,0))]
    context = {
        "tikz_instructions": tikz_instructions,
        "canvas_width": generation_config.GenerationConfig.canvas_width,
        "canvas_height": generation_config.GenerationConfig.canvas_height,
    }
    output = template.render(context)

    latex_filename = (
        f"{generation_config.GenerationConfig.generated_file_prefix}{n}.tex"
    )
    with open(f"./output_tex/{latex_filename}", "w", encoding="utf-8") as f:
        f.write(output)

    json_filename = (
        f"{generation_config.GenerationConfig.generated_file_prefix}{n}.json"
    )
    with open(f"./output_json/{json_filename}", "w", encoding="utf-8") as f:
        # json.dump([item.to_dict() for item in panels],f,indent=4)
        json.dump(
            [panel.__dict__ for panel in panels],
            f,
            indent=4,
            default=lambda x: x.to_dict(),
        )


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1]:
        generation_config.GenerationConfig.generate_num = int(sys.argv[1])
    if len(sys.argv) >= 3 and sys.argv[2]:
        generation_config.GenerationConfig.color_mode = sys.argv[2]
    if len(sys.argv) >= 4 and sys.argv[3]:
        generation_config.GenerationConfig.generated_file_prefix = sys.argv[3]
    for i in range(generation_config.GenerationConfig.generate_num):
        main(i)
