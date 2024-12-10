from typing import List
from entities.entity import Relationship
from entities.simple_shape import SimpleShape
from entities.touching_point import TouchingPoint

class Panel():
    def __init__(self,top_left:list[float],bottom_right:list[float],shapes:SimpleShape,joints:List[Relationship]) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.shapes = shapes
        self.joints = joints