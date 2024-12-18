
from typing import List
from shapely import unary_union

from entities.entity import VisibleShape


class ShapeGroup:
    def __init__(self,shapes:List[List[VisibleShape]]) -> None:
        self.shapes = shapes
        
    def geometry(self,layer):
        return unary_union([shape.base_geometry for shape in self.shapes[layer]])
    
    def add(self,new_shapes:List[List[VisibleShape]]):
        for layer,shapes in enumerate(new_shapes):
            while layer >= len(self.shapes):
                self.shapes.append([])
            self.shapes[layer] += shapes
