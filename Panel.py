from SimpleShape import SimpleShape
from TouchingPoint import TouchingPoint

class Panel():
    def __init__(self,top_left:list[float],bottom_right:list[float],shapes:SimpleShape,joints:TouchingPoint) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right
        self.shapes = shapes
        self.joints = joints