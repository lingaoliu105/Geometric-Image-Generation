from Panel import Panel
import img_params
from SimpleShape import SimpleShape

def get_pattern_tikz_string(pattern: img_params.Pattern) -> str:
    lookup_dict = {
        img_params.Pattern.NIL: "none",
        img_params.Pattern.DOT: "dots",
        img_params.Pattern.NEL: "north east lines",
        img_params.Pattern.NWL: "north west lines",
        img_params.Pattern.VERTICAL: "vertical lines",
        img_params.Pattern.HORIZONTAL: "horizontal lines",
        img_params.Pattern.CROSSHATCH: "crosshatch",
        img_params.Pattern.BRICK: "bricks",
    }
    return lookup_dict[pattern]


def convert_shape(input_shape: SimpleShape):
    tikz_instruction = ""
    shape, pos_x, pos_y, rotation, size, color_stm, pattern = (
        input_shape.shape,
        input_shape.position[0],
        input_shape.position[1],
        input_shape.rotation,
        input_shape.size,
        f"black!{input_shape.color.value}!white",
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


def convert_shapes(input_shapes: list[SimpleShape]) -> list[str]:
    instructions = []
    for shape in input_shapes:
        instructions.append(convert_shape(shape)) 
    return instructions

def convert_panels(panels:list[Panel]) -> list[str]:
    instructions = []
    for panel in panels:
        instructions += convert_shapes(panel.shapes)
        
        # TODO: remove this after use
        for touchingpt in panel.joints:
            pos = touchingpt.position
            instructions.append(format_node_instruction(pos[0],pos[1],0.1,"black",8,"None",0))

    return instructions


def format_node_instruction(
    pos_x, pos_y, size, color_stm: str, sides: int, pattern: str, rotation: int = 0
):  # \node is used to draw regular shapes
    base_instruction = f"\\node[regular polygon, regular polygon sides={sides}, minimum size={size}cm, inner sep=0pt, draw,rotate={rotation},pattern={pattern}] at ({pos_x},{pos_y}) {{}};"
    return base_instruction
