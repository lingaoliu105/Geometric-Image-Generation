from typing import Optional
from img_params import *
import math
import random
import numpy as np

import img_params
from shapely.geometry import Point, LineString, Polygon


class SimpleShape():

    __slots__=["shape","size","position","pattern","rotation","color","base_geometry"]
    def __init__(
        self,
        position: np.ndarray,
        rotation: float,
        size: Optional[int] = None,
        shape: Optional[img_params.Shape] = None,
        color: Optional[img_params.Color] = None,
        pattern: Optional[img_params.Pattern] = None,
    ) -> None:
        self.position = position
        self.rotation = rotation
        self.shape = (
            shape if shape is not None else random.choice(list(img_params.Shape))
        )
        self.size = (
            size if size is not None else random.choice(list(img_params.Size))
        )
        self.color = (
            color if color is not None else random.choice(list(img_params.Color))
        )
        self.pattern = (
            pattern if pattern is not None else random.choice(list(img_params.Pattern))
        )
        self.compute_base_geometry()

    def compute_base_geometry(self):
        rot_rad = math.radians(self.rotation)
        rot_sin = math.sin(rot_rad)
        rot_cos = math.cos(rot_rad)
        rot_polar = np.array((rot_cos, rot_sin))
        rot_cart = self.size.value * rot_polar
        if self.shape == Shape.LINE:
            size = self.size.get_actual(self.shape)
            endpoints = [
                np.array(x)
                for x in [
                    (
                        self.position[0] + size // 2 * rot_cos,
                        self.position[1] + size // 2 * rot_sin,
                    ),
                    (
                        self.position[0] - size // 2 * rot_cos,
                        self.position[1] - size // 2 * rot_sin,
                    ),
                ]
            ]
            self.base_geometry = LineString(endpoints)

        # TODO: complete other shapes. remember to add last -- first
        elif self.shape == Shape.CIRCLE:
            self.base_geometry = Point(self.position).buffer(self.size)
        else:
            if self.shape == Shape.TRIANGLE_EQ:
                angle_list = [-30, 90, 210]
            elif self.shape == Shape.SQUARE:
                angle_list = [-45, 45, 135, 225]
            elif self.shape == Shape.PENTAGON:
                angle_list = [-54 + 72 * x for x in range(5)]
            elif self.shape == Shape.HEXAGON:
                angle_list = [60 * x for x in range(6)]

            vertices = [None] * (len(angle_list))
            index = 0
            for angle in angle_list:
                rot_rad = math.radians(angle)
                rot_sin = math.sin(rot_rad)
                rot_cos = math.cos(rot_rad)
                rot_polar = np.array((rot_cos, rot_sin))
                rot_cart = self.size.value * rot_polar
                vertices[index] = self.position + rot_cart
                index += 1
            self.base_geometry = Polygon(vertices)

    def get_vertices(self) -> list:
        return self.base_geometry.exterior.coords

    def get_attach_point(self)->np.ndarray:
        if self.shape==Shape.CIRCLE:
            rand_rad = random.random()*2*math.pi
            return self.position + self.size.value * np.array([math.cos(rand_rad),math.sin(rand_rad)])
        fraction = random.choice(list(TouchingPoint)).value*random.randint(1,5)%1
        vertices = self.get_vertices()
        edge_index = random.randint(0,len(vertices)-2) # the edge is vert[index] -- vert[index+1]
        return vertices[edge_index]+fraction*(vertices[edge_index+1]-vertices[edge_index])
    
    def check_overlap(self,other:"SimpleShape")->bool:
        return self.base_geometry.overlaps(other.base_geometry)
