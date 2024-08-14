import random
from jinja2 import Environment, FileSystemLoader

import img_params
import sys

generate_num = 10


def combine_simple_images():
    layout = random.choice(list(img_params.Layout))
    panel_num = int(layout.value)
    instructions = []
    # for each panel, draw simple shapes
    for i in range(panel_num):
        pos = compute_panel_position(layout, i)
        rot = random.choice(list(img_params.Rotation)).value * random.randint(0, 23)
        instructions.append(generate_simple_image(pos[0], pos[1], rot))
    return instructions


def compute_panel_position(layout, index):
    """
    arguments:
    layout(Layout): the layout of the image
    index(int): the index of the panel to compute, starting from 0

    output:
    (float, float): the x-coordinate and y-coordinate of the center of the panel (assume the whole image is 20cm x 20cm)
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
    return lookup_table[layout][index]


def generate_simple_image(pos_x, pos_y, rotation):
    """
    arguments:
    pos_x and pos_y (int or float):  define the position of the center,
    rotation (int or float): the counter-clockwise rotation in degree

    returns
    str: the tikz instruction to draw a random simple geometry object.
    """
    shape = random.choice(list(img_params.Shape))
    size_item = random.choice(list(img_params.Size))
    size = size_item.value
    color = random.choice(list(img_params.Color))
    color_stm = f"white!{color.value}!black"
    pattern = {
        img_params.Pattern.NIL: "",
        img_params.Pattern.DOT: "dots",
        img_params.Pattern.NEL: "north east lines",
        img_params.Pattern.NWL: "north west lines",
        img_params.Pattern.VERTICAL: "vertical lines",
        img_params.Pattern.HORIZONTAL: "horizontal lines",
        img_params.Pattern.CROSSHATCH: "crosshatch",
        img_params.Pattern.BRICK: "bricks",
    }[random.choice(list(img_params.Pattern))]

    tikz_instruction = ""
    if shape == img_params.Shape.LINE:
        tikz_instruction = f"\draw ({pos_x}, {pos_y})--++({rotation}:{size});\n\draw ({pos_x},{pos_y})--++({rotation}:{-size});\n"
    elif shape == img_params.Shape.CIRCLE:
        tikz_instruction = (
            f"\draw [fill={color_stm}] ({pos_x},{pos_y}) circle ({size});\n"
        )
        if pattern != "":
            tikz_instruction += f"\draw [fill={color_stm},pattern={pattern}] ({pos_x},{pos_y}) circle ({size});\n"
    elif (
        shape == img_params.Shape.TRIANGLE_EQ
        or shape == img_params.Shape.SQUARE
        or shape == img_params.Shape.PENTAGON
        or shape == img_params.Shape.HEXAGON
    ):
        tikz_instruction = format_node_instruction(
            pos_x,
            pos_y,
            size,
            color_stm,
            int(shape.value),
            pattern=pattern,
            rotation=rotation,
        )

    return tikz_instruction


def format_node_instruction(
    pos_x, pos_y, size, color_stm: str, sides: int, pattern: str = "", rotation: int = 0
):  # \node is used to draw regular shapes
    base_instruction = f"\\node[regular polygon, regular polygon sides={sides}, minimum size={size}cm, draw, rotate={rotation},fill={color_stm}] at ({pos_x},{pos_y}) {{}};"
    pattern_instruction = f"\\node[regular polygon, regular polygon sides={sides}, minimum size={size}cm, draw,rotate={rotation},pattern={pattern}] at ({pos_x},{pos_y}) {{}};"
    if pattern != "":
        base_instruction += pattern_instruction
    return base_instruction


def main(n):
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template("tikz_template.jinja")
    tikz_instructions = combine_simple_images()
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
