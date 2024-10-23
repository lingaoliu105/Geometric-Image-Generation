# The enumeration classes of different image parameters

from enum import Enum


class Shape(
    Enum
):  # representing categories under A_type, value normally indicates the number of edges
    LINE = 0
    circle = 1
    triangle = 3
    square = 4
    pentagon = 5
    hexagon = 6
    # dot = 
    # linesegment =
    # triangle =
    # square =
    # rectangle =
    # pentagon =
    # hexagon =
    # heptagon =
    # octagon =
    # nonagon =
    # decagon =
    # circle =
    # ellipse =
    # star =
    # diamond =


class Color(Enum):  # color from white to black, 9 levels
    # white = 0
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
    blank = 0
    horizontalLines = 1
    verticalLines = 2
    northEastLines = 3
    northWestLines = 4
    grid = 5
    crosshatch = 6
    dots = 7
    crosshatchDots = 8
    fivepointedStars = 9
    sixpointedStars = 10
    bricks = 11
    checkerboard = 12


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

class HorizontalPosition(Enum):
    """Given a single entity, this supercategory represents the horizontal position
    of that entity, relative to the panel that the entity belongs to
    """
    left=0
    nearLeft=1
    leftwards=2
    slightlyLeftwards=3
    horizontalMiddle=4
    slightlyRightwards=5
    rightwards=6
    nearRight=7
    right=8

class  VerticalPosition(Enum):
    """Given a single entity, this supercategory represents the vertical position of
    that entity, relative to the panel that the entity belongs to.
    """
    top=0
    nearTop=1
    high=2
    slightlyHigher=3
    verticalMiddle=4
    slightlyLower=5
    low=6
    nearBottom=7
    bottom=8
