from SimpleShape import SimpleShape
from TouchingPoint import TouchingPoint

class Panel():
    def __init__(self,shapes:SimpleShape,joints:TouchingPoint) -> None:
        self.shapes = shapes
        self.joints = joints