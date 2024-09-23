from enum import Enum
import json
import math

import numpy as np

from SimpleShape import SimpleShape

from shapely_helpers import *

import img_params
from typing import Tuple
from Entity import Entity


class TouchingPoint(Entity):
    __slots__ = [
        "position",
        "neighbor_A",  # how to order A and B: compare left/right first, left is A right is B,if same, up is A, down is B
        "neighbor_B",
        "attach_type_A",  # edge, corner or arc
        "attach_type_B",
        "attach_position_A",  # top, near-top, middle, bottom, near-bottom, only applicable when attach_type_A is edge
        "attach_position_B",
    ]

    def __init__(self,neighbor1:SimpleShape,neighbor2:SimpleShape):
        center1 = neighbor1.position
        center2 = neighbor2.position
        if center1[0]<center2[0]:
            self.neighbor_A,self.neighbor_B = neighbor1,neighbor2  # convert to uid while serializing
        elif math.abs(center1[0]-center2[0])<1e-10:
            if center1[1]>center2[1]:
                self.neighbor_A,self.neighbor_B = neighbor1,neighbor2
            else:
                self.neighbor_A, self.neighbor_B = neighbor2, neighbor1
        else:
            self.neighbor_A, self.neighbor_B = neighbor2, neighbor1

        self.position = find_touching_point(neighbor1,neighbor2).coords[0]

        # compute how the point connects neighbor_A and neighbor_B
        self.attach_type_A,self.attach_position_A = self.compute_neighbor_relation(self.neighbor_A)
        self.attach_type_B,self.attach_position_B = self.compute_neighbor_relation(self.neighbor_B)

    def compute_neighbor_relation(self,neighbor:SimpleShape)->Tuple[img_params.AttachType,img_params.AttachPosition]:
        if neighbor.shape==img_params.Shape.circle:
            return (img_params.AttachType.ARC,img_params.AttachPosition.NA)
        elif neighbor.shape in [img_params.Shape.triangle,img_params.Shape.square,img_params.Shape.pentagon,img_params.Shape.hexagon]:
            # first check if the point is on corner
            neighbor_vertices = neighbor.base_geometry.exterior.coords
            buffered_point = Point(self.position).buffer(0.01)
            for vertex in neighbor_vertices:
                if buffered_point.contains(Point(vertex)):
                    return (img_params.AttachType.CORNER,img_params.AttachPosition.NA)
            edge = find_edge_with_point(neighbor.base_geometry,Point(self.position))
            endpoints = edge.coords
            upper_vertex, lower_vertex = (
                endpoints[0],endpoints[1]) if endpoints[0][1] > endpoints[1][1] else (endpoints[1],endpoints[0])
            try:
                fraction = (upper_vertex[1] - self.position[1]) / (upper_vertex[1]-lower_vertex[1])
                position = min(img_params.AttachPosition, key=lambda x:abs(x.value-fraction))
            except ZeroDivisionError: # happens when the edge is horizontal
                position = img_params.AttachPosition.TOP #TODO: find more proper description
            return (img_params.AttachType.EDGE,position)
