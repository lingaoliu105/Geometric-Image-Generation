 # The enumeration classes of different image parameters

from enum import Enum

class Shape (Enum): #representing categories under A_type, value normally indicates the number of edges
    LINE = 0
    CIRCLE = 1
    TRIANGLE_EQ = 3
    SQUARE = 4
    PENTAGON = 5
    HEXAGON = 6

class Layout (Enum):
    SINGLE = 1
    LR = 2.0 # left -- right
    UD = 2.1 # up -- down
    FEFT = 4.0 # the strange 5842 layout
    QUADRANT = 4.1 # 2x2
    GRID = 9 # 3x3

class Size (Enum): # relative size of each component
    S = 1
    M = 1.5
    L = 2
    XL = 2.5

class Color(Enum): # color from white to black, 9 levels
    value_difference = 100 / 8
    
    C1 = 0
    C2 = int(value_difference * 1)
    C3 = int(value_difference * 2)
    C4 = int(value_difference * 3)
    C5 = int(value_difference * 4)
    C6 = int(value_difference * 5)
    C7 = int(value_difference * 6)
    C8 = int(value_difference * 7)
    C9 = 100

class Rotation(Enum): # only 2 types. actual rotation will be random times the basic angle
    ANGLE30 = 30
    ANGLE45 = 45