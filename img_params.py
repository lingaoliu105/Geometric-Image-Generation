# The enumeration classes of different image parameters

from enum import Enum


class Shape(
    Enum
):  # representing categories under A_type, value normally indicates the number of edges
    LINE = 0
    CIRCLE = 1
    TRIANGLE_EQ = 3
    SQUARE = 4
    PENTAGON = 5
    HEXAGON = 6


class Layout(Enum):
    SINGLE = 1
    LR = 2.0  # left -- right
    UD = 2.1  # up -- down
    FEFT = 4.0  # the strange 5842 layout
    QUADRANT = 4.1  # 2x2
    GRID = 9  # 3x3


class Color(Enum):  # color from white to black, 9 levels
    white = 0
    black = 1
    red = 2
    green = 3
    blue = 4
    cyan = 5
    magenta = 6
    yellow = 7
    purple = 8
    brown = 9
    orange = 10


class Rotation(
    Enum
):  # only 2 types. actual rotation will be random times the basic angle
    ANGLE30 = 30
    ANGLE45 = 45


class Pattern(Enum):  # the pattern (dots, lines, etc) that fills up the shape
    NIL = -1
    DOT = 0
    NEL = 1
    NWL = 2
    VERTICAL = 3
    HORIZONTAL = 4
    CROSSHATCH = 5
    BRICK = 6


class Composition(Enum):
    SIMPLE = 0
    CHAIN = 1
    NESTING = 2


class TouchingPosition(Enum):
    ENDPOINT = 0
    MIDDLE = 0.5
    THIRD = 0.33
    QUARTER = 0.25
    FIFTH = 0.2


class AttachType(Enum):
    """defines how 1 shape touches the other."""

    EDGE = 0
    ARC = 1
    CORNER = 2


class AttachPosition(Enum):
    TOP = 0
    NEAR_TOP = 0.25
    MIDDLE = 0.5
    NEAR_BOTTOM = 0.75
    BOTTOM = 1
    NA = -1  # not applicable, used for arc and corner


class Lightness(Enum):
    lightness20 = 20
    lightness25 = 25
    lightness33 = 33
    lightness40 = 40
    lightness50 = 50
    lightness60 = 60
    lightness67 = 67
    lightness75 = 75
    lightness80 = 80
    lightness100 = 100


class PattenColor(Enum):
    patternWhite = 0
    patternBlack = 1
    patternRed = 2
    patternGreen = 3
    patternBlue = 4
    patternCyan = 5
    patternMagenta = 6
    patternYellow = 7
    patternPurple = 8
    patternBrown = 9
    patternOrange = 10


class PatternLightness(Enum):
    patternLightness20 = 20
    patternLightness25 = 25
    patternLightness33 = 33
    patternLightness40 = 40
    patternLightness50 = 50
    patternLightness60 = 60
    patternLightness67 = 67
    patternLightness75 = 75
    patternLightness80 = 80
    patternLightness100 = 100


class Outline(Enum):
    solid = 0
    dotted = 1
    denselyDotted = 2
    looselyDotted = 3
    dashed = 4
    denselyDashed = 5
    looselyDashed = 6
    dashDot = 7
    denselyDashDot = 8
    dashDotDot = 9
    denselyDashDotDot= 10
    looselyDashDotDot = 11


class OutlineColor(Enum):
    outlineWhite = 0
    outlineBlack = 1
    outlineRed = 2
    outlineGreen = 3
    outlineBlue = 4
    outlineCyan = 5
    outlineMagenta = 6
    outlineYellow = 7
    outlinePurple = 8
    outlineBrown = 9
    outlineOrange = 10


class OutlineLightness(Enum):
    outlineLightness20 = 20
    outlineLightness25 = 25
    outlineLightness33 = 33
    outlineLightness40 = 40
    outlineLightness50 = 50
    outlineLightness60 = 60
    outlineLightness67 = 67
    outlineLightness75 = 75
    outlineLightness80 = 80
    outlineLightness100 = 100


class OutlineThickness(Enum):
    noOutline = 0
    ultraThin = 1
    veryThin = 2
    thin = 3
    semithick = 4
    thick = 5
    veryThick = 6
    ultraThick = 7
