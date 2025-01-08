from typing import List, Optional, Union
import numpy as np
from shapely import unary_union

from entities.complex_shape import ComplexShape
from entities.visible_shape import VisibleShape
from generation_config import GenerationConfig
import img_params
from panel import Panel


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

    def add_group(self,new_shapes:Union[List[List[VisibleShape]],"ShapeGroup"]):
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
        self.pad_layer(self.layer_num + layer + 1) 
        overlapping_group = [[] for _ in range(len(self.shapes))]        
        for layer_cnt in range(len(self.shapes)):
            if shape.base_geometry.overlaps(self.geometry(layer_cnt)):
                overlapping_group[layer_cnt+layer+1].extend(ComplexShape.from_overlapping_geometries(shape.base_geometry,self.geometry(layer_cnt)))

        for layer_cnt,shapes in enumerate(overlapping_group):
            self.shapes[layer_cnt].extend(shapes)
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

    def shift(self,offset):
        if not isinstance(offset,np.ndarray):
            offset = np.array(offset)
        for layer in self.shapes:
            for shape in layer:
                shape.shift(offset)

    @property
    def center(self):
        coordinates = [shape.center for shape in self.shapes[0]]
        # 将坐标转换为 numpy 数组
        coords_array = np.array(coordinates)

        # 计算平均值
        avg_x = np.mean(coords_array[:, 0])
        avg_y = np.mean(coords_array[:, 1])

        return np.array([avg_x, avg_y])

    def rotate(self, angle:img_params.Angle, origin="center"):
        if origin == "center":
            origin = self.center

        for layer in self.shapes:
            for shape in layer:
                shape.rotate(angle, origin)

    def size(self):
        return sum([len(layer) for layer in self.shapes])

    def scale(self,scale_ratio,origin="center"):
        if origin == "center":
            origin = self.center
        for layer in self.shapes:
            for shape in layer:
                shape.scale(scale_ratio,origin)

    def to_panel(self,top_left,bottom_right):
        '''place the shape group in a panel. shape group is by default placed on the entire canvas, and will be shifted and shrinked to fit in the panel'''
        panel_center = ((top_left[0]+bottom_right[0])/2,(top_left[1]+bottom_right[1])/2)
        self.shift(panel_center)
        scale_ratio = (bottom_right[0]-top_left[0]) / (GenerationConfig.right_canvas_bound - GenerationConfig.left_canvas_bound)
        assert scale_ratio == (top_left[1]-bottom_right[1]) / (GenerationConfig.upper_canvas_bound - GenerationConfig.lower_canvas_bound)
        self.scale(scale_ratio=scale_ratio)
        flattened_list = [item for sublist in self.shapes for item in sublist]
        return Panel(top_left=top_left,bottom_right=bottom_right,shapes=flattened_list,joints=[])

    def show(self):
        for layer in self.shapes:
            print([f"{shape.__class__.__name__}, uid: {shape.uid}" for shape in layer])
