import json
import math
import random
import sys
from pathlib import Path
from typing import List, Literal

import jsonref
import numpy as np
import shapely
from jinja2 import Environment, FileSystemLoader

import img_params
from entities.line_segment import LineSegment
from entities.simple_shape import SimpleShape
from entities.touching_point import TouchingPoint
from generation_config import GenerationConfig
from image_generators import (BorderImageGenerator,
                                     ChainingImageGenerator,
                                     EnclosingImageGenerator,
                                     ParallelImageGenerator,
                                     RandomImageGenerator,
                                     SimpleImageGenerator,
                                     generate_shape_group, get_image_generator)
from input_configs import BaseConfig
from panel import Panel
from shape_group import ShapeGroup
from tikz_converters import *
from util import *


def generate_panels(base_config:BaseConfig) -> list[Panel]:
    """combine images of each sub-panel"""
    layout = GenerationConfig.layout
    row_num = layout[0]
    col_num = layout[1]
    panel_num = row_num * col_num
    
    panels = []
    # for each panel, draw simple shapes
    for i in range(panel_num):
        reconfigure_for_panel(i)
        print(f"Generating panel {i+1}/{panel_num}")

        center, top_left, bottom_right = compute_panel_position(layout, i)
        elements = generate_shape_group()
        
        panel = elements.to_panel(top_left=top_left,bottom_right=bottom_right)
        panels.append(panel)
    
    return panels
 
def reconfigure_for_panel(panel_index):
    while not isinstance(GenerationConfig.current_config, BaseConfig):
        GenerationConfig.current_config = GenerationConfig.current_config.parent
    GenerationConfig.current_config = GenerationConfig.current_config.panel_configs[panel_index]

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

        line_seg = LineSegment(pt1 = min(init,end,key=comp_key),pt2 = max(init,end,key=comp_key))
        output_line_segments.append(line_seg)
        init = end
        
    actual_center = np.array([(left_bound+right_bound)/2,(upper_bound+lower_bound)/2])
    offset = position - actual_center
    for l in output_line_segments:
        l.shift(offset)
    return output_line_segments


def main(n):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("tikz_template.jinja")
    base_config = initialize_config()
    panels = generate_panels(base_config)
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

def initialize_config()->BaseConfig:
    base_path = Path("input/base.json").resolve()

    # 加载主文件并解析引用
    with open(base_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    resolved = jsonref.JsonRef.replace_refs(data,base_uri=base_path.as_uri())
    global_basic_attributes_distribution = json.load(open("input/basic_attributes_distribution.json","r",encoding="utf-8"))
    resolved = resolved | global_basic_attributes_distribution

    resolved_json_str = json.dumps(resolved,indent=4)
    config = BaseConfig.model_validate_json(resolved_json_str)
    GenerationConfig.current_config = config
    return config


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1]:
        generation_config.GenerationConfig.generate_num = int(sys.argv[1])
    if len(sys.argv) >= 3 and sys.argv[2]:
        generation_config.GenerationConfig.color_mode = sys.argv[2]
    if len(sys.argv) >= 4 and sys.argv[3]:
        generation_config.GenerationConfig.generated_file_prefix = sys.argv[3]
    for i in range(generation_config.GenerationConfig.generate_num):
        main(i)
