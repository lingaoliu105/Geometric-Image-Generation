from typing import List
from shapely import unary_union

from entities.complex_shape import ComplexShape
from entities.entity import VisibleShape


class ShapeGroup:
    def __init__(self,shapes:List[List[VisibleShape]]) -> None:
        self.shapes = shapes if shapes is not None else [[]]
        self.union_geometries = []

    def geometry(self,layer):
        # to keep geometries list updated
        self.pad_layer(layer)
        self.union_geometries[layer] = unary_union([shape.base_geometry for shape in self.shapes[layer]])
        return self.union_geometries[layer]

    def pad_layer(self,layer):
        '''make the shape group contain up to the given layer (starting from 0)'''
        while layer >= len(self.shapes):
            self.shapes.append([])
        while layer >= len(self.union_geometries):
            self.union_geometries.append([])

    def add_group(self,new_shapes:List[List[VisibleShape]]):
        if isinstance(new_shapes,ShapeGroup):
            new_shapes = new_shapes.shapes
            
        def validate_two_level_list(lst):
            if not isinstance(lst, list):
                raise ValueError("The input must be a list.")

            for item in lst:
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, list):
                            raise ValueError("The list cannot be nested more than two levels.")
        validate_two_level_list(new_shapes)
        self.pad_layer(len(self.shapes)+len(new_shapes)) # total layer depends on the sum of max layer of 2 groups
        for new_layer,shapes_on_layer in enumerate(new_shapes):
            for shape in shapes_on_layer:
                self.add_shape_on_layer(shape,new_layer)                
    def add_shape(self,shape:VisibleShape):
        self.add_shape_on_layer(shape,0)
        
    @property
    def layer_num(self):
        return len(self.shapes)
    
    def add_shape_on_layer(self,shape:VisibleShape,layer:int):
        '''layer starts from 0'''
        self.pad_layer(self.layer_num + layer)
        overlapping_group = [[]] * len(self.shapes)
        for layer_cnt in range(len(self.shapes)):
            if shape.base_geometry.overlaps(self.geometry(layer_cnt)):
                overlapping_group[layer_cnt+layer]+=(ComplexShape.from_overlapping_geometries(shape.base_geometry,self.union_geometries[layer_cnt]))
                
        for layer_cnt,shapes in enumerate(overlapping_group):
            self.shapes[layer_cnt] += shapes
        self.shapes[layer].append(shape)
        
    def __add__(self,other):
        if isinstance(other,VisibleShape):
            self.add_shape(other)
        elif isinstance(other,ShapeGroup):
            self.add_group(other.shapes)
        elif isinstance(other,list) and all(isinstance(item, VisibleShape) for item in other):
            self.add_group([other])
        elif isinstance(other,list) and all(isinstance(item, list) for item in other):
            self.add_group(other)
        else:
            raise ValueError("Unsupported item to add to ShapeGroup")
        return self
        
    def __len__(self):
        return len(self.shapes)

    def __getitem__(self,key):
        return self.shapes[key]
