from typing import List
from entities.entity import Relationship
from entities.simple_shape import SimpleShape
from entities.touching_point import TouchingPoint
from entities.visible_shape import VisibleShape

class Panel():
    def __init__(self,top_left:list[float],bottom_right:list[float],shapes:List[VisibleShape],joints:List[Relationship]) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.shapes = shapes
        self.joints = joints