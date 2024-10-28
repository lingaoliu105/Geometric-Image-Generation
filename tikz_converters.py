import re
import entities.entity as entity
from img_params import *
from abc import ABC, abstractmethod

class BaseConverter: # enclose in classes to store temporary strings that makes the tikz strings
    def __init__(self) -> None:
        self.color_str = ""
        self.lightness_str = ""
        
    def partition_camel_case(self,string):
        return re.sub(r"([a-z])([A-Z])", r"\1 \2", string).lower()
    
    @abstractmethod
    def convert(self,target:entity.Entity):
        pass
        
class SimpleShapeConverter(BaseConverter):
    def __init__(self) -> None:
        super().__init__()
        self.pattern_str = ""
        self.pattern_color_str = ""
        self.pattern_lightness_str = ""
        self.outline_str = ""
        self.outline_color_str = ""
        self.outline_thickness_str = ""
        self.outline_lightness_str = ""

    def convert(self, shape):

        func_router = {
            "pattern": self.get_pattern_tikz_string,
            "color": self.get_color_tikz_string,
            "lightness": self.get_lightness_tikz_string,
            "pattern_color": self.get_pattern_color_tikz_string,
            "pattern_lightness": self.get_pattern_lightness_string,
            "outline": self.get_outline_tikz_string,
            "outline_color": self.get_outline_color_tikz_string,
            "outline_thickness": self.get_outline_thickness_tikz_string,
            "outline_lightness": self.get_outline_lightness_tikz_string,
        }

        for attr in shape.__slots__:
            if attr in func_router:
                func_router[attr](getattr(shape, attr))

        if shape.shape in [
            Shape.triangle,
            Shape.square,
            Shape.pentagon,
            Shape.hexagon,
        ]:
            sides = shape.shape.value
            return (
                # draw the background color in seperate instruction, otherwise will be covered by pattern
                f"\\node[regular polygon, regular polygon sides={sides}, minimum size={round(shape.size,3)}cm,"
                f"{self.color_str+self.lightness_str}, inner sep=0pt,rotate={shape.rotation}]"
                f"at ({shape.position[0]},{shape.position[1]}) {{}};\n"
                
                f"\\node[{self.outline_thickness_str},regular polygon, regular polygon sides={sides}, minimum size={round(shape.size,3)}cm,"
                f"inner sep=0pt,{self.outline_color_str+self.outline_lightness_str},rotate={shape.rotation},{self.pattern_str},"
                f"{self.pattern_color_str+self.pattern_lightness_str},{self.outline_str}] at ({shape.position[0]},{shape.position[1]}) {{}};\n"
            )
        elif shape.shape == Shape.circle:
            return (
                f"\draw [{self.color_str+self.lightness_str}]"
                f"({shape.position[0]},{shape.position[1]}) circle ({shape.size});\n"

                f"\draw [{self.outline_thickness_str},{self.outline_color_str},{self.outline_str},"
                f"{self.pattern_str},{self.pattern_color_str+self.pattern_lightness_str}]"
                f"({shape.position[0]},{shape.position[1]}) circle ({shape.size});\n"
            )


    def get_pattern_tikz_string(self, pattern: Pattern):
        if pattern==Pattern.blank:
            return
        self.pattern_str = f"pattern={self.partition_camel_case(pattern.name)}"

    def get_pattern_lightness_string(
        self, pattern_lightness: PatternLightness
    ):
        self.pattern_lightness_str = f"!{pattern_lightness.value}"

    def get_pattern_color_tikz_string(self, patttern_color: PattenColor):
        self.pattern_color_str = f"pattern color={patttern_color.name.removeprefix('pattern').lower()}"

    def get_color_tikz_string(self, color: Color):
        self.color_str = f"fill={color.name}"

    def get_lightness_tikz_string(self, lightness: Lightness):
        self.lightness_str = f"!{lightness.value}"

    def get_outline_tikz_string(self, outline: Outline):
        self.outline_str = self.partition_camel_case(outline.name)

    def get_outline_color_tikz_string(self, outline_color: OutlineColor):
        self.outline_color_str = (
            f"draw={outline_color.name.removeprefix('outline').lower()}"
        )

    def get_outline_lightness_tikz_string(
        self, outline_lightness: OutlineLightness
    ):
        self.outline_lightness_str = f"!{outline_lightness.value}"

    def get_outline_thickness_tikz_string(
        self, outline_thickness: OutlineThickness
    ):
        if outline_thickness == OutlineThickness.noOutline:
            self.outline_str = "draw=none"
            return
        self.outline_thickness_str = f"line width={outline_thickness.value*0.1}mm"

class LineSegmentConverter(BaseConverter):
    def __init__(self) -> None:
        super().__init__()
        
    def convert(self, target):
        tikz = f"\draw[color={target.color.name.lower()}] ({target.endpt_lu[0]},{target.endpt_lu[1]}) -- ({target.endpt_rd[0]},{target.endpt_rd[1]});"
        return tikz
        
    
def convert_shapes(input_shapes, show_center: bool) -> list[str]:
    instructions = []
    for shape in input_shapes:
        converter = SimpleShapeConverter()
        instructions.append(converter.convert(shape))

    return instructions


def convert_panels(panels) -> list[str]:
    instructions = []
    for panel in panels:
        instructions += convert_shapes(panel.shapes, False)

        # TODO: remove this after use
        for touchingpt in panel.joints:
            pos = touchingpt.position

    return instructions
