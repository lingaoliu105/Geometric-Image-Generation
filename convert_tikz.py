import img_params
from SimpleShape import SimpleShape

def get_pattern_tikz_string(pattern: img_params.Pattern) -> str:
    lookup_dict = {
        img_params.Pattern.NIL: "",
        img_params.Pattern.DOT: "dots",
        img_params.Pattern.NEL: "north east lines",
        img_params.Pattern.NWL: "north west lines",
        img_params.Pattern.VERTICAL: "vertical lines",
        img_params.Pattern.HORIZONTAL: "horizontal lines",
        img_params.Pattern.CROSSHATCH: "crosshatch",
        img_params.Pattern.BRICK: "bricks",
    }
    return lookup_dict[pattern]


def convert_tikz_instruction(input_shape: SimpleShape):
    tikz_instruction = ""
    shape, pos_x, pos_y, rotation, size, color_stm, pattern = (
        input_shape.shape,
        input_shape.position[0],
        input_shape.position[1],
        input_shape.rotation,
        input_shape.size,
        f"white!{input_shape.color.value}!black",
        get_pattern_tikz_string(input_shape.pattern),
    )

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


def convert_tikz_instructions(input_shapes: list):
    instruction = ""
    for shape in input_shapes:
        instruction += convert_tikz_instruction(shape)
    return instruction


def format_node_instruction(
    pos_x, pos_y, size, color_stm: str, sides: int, pattern: str = "", rotation: int = 0
):  # \node is used to draw regular shapes
    base_instruction = f"\\node[regular polygon, regular polygon sides={sides}, minimum size={size}cm, draw, rotate={rotation},fill={color_stm}] at ({pos_x},{pos_y}) {{}};"
    pattern_instruction = f"\\node[regular polygon, regular polygon sides={sides}, minimum size={size}cm, draw,rotate={rotation},pattern={pattern}] at ({pos_x},{pos_y}) {{}};"
    if pattern != "":
        base_instruction += pattern_instruction
    return base_instruction
