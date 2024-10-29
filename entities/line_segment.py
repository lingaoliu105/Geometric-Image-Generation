import copy
import random
import numpy as np
from shapely import LineString
import common_types
from entities.entity import Entity, OpenShape
from typing import Optional, Union

import generation_config
import img_params
from tikz_converters import LineSegmentConverter
from uid_service import get_new_entity_uid
from util import get_rand_point, rotate_point
from shapely.affinity import translate



class LineSegment(OpenShape):
    direct_categories = [
        "color",
        "lightness",
    ]  # attributes that can be directly interpreted as categories in dataset annotations

    __slots__ = [
        "uid",
        "base_geometry",
    ] + direct_categories
    
    endpt_comp_key = lambda p: (p[0], -p[1])

    def __init__(
        self,
        pt1: Optional[Union[np.ndarray, tuple, list]] = None,
        pt2: Optional[Union[np.ndarray, tuple, list]] = None,
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
    ) -> None:
        super().__init__(tikz_converter=LineSegmentConverter())
        if pt1 is None and pt2 is None:
            # if neither points is specified, choose both points randomly
            self.base_geometry = LineString([get_rand_point() for _ in range(2)])
        elif pt1 is None:
            self.base_geometry = LineString([pt2, get_rand_point()])
        elif pt2 is None:
            self.base_geometry = LineString([pt1, get_rand_point()])
        else:
            self.base_geometry = LineString([pt1,pt2])

        self.color = (
            color if color is not None else random.choice(list(img_params.Color))
        )
        self.lightness = (
            lightness
            if lightness is not None
            else random.choice(list(img_params.Lightness))
        )
        
        
    @property
    def endpt_lu(self):
        endpt_coords = self.base_geometry.coords
        assert len(endpt_coords)==2
        pt1,pt2 = endpt_coords
        return min(pt1,pt2,self.endpt_comp_key)

    @property
    def endpt_rd(self):
        endpt_coords = self.base_geometry.coords
        assert len(endpt_coords)==2
        pt1,pt2 = endpt_coords
        return max(pt1,pt2,self.endpt_comp_key)

    def shift(self,offset:np.ndarray):
        self.base_geometry = translate(self.base_geometry,offset[0],offset[1])
        
    def set_endpoints(self,pt1:common_types.Coordinate,pt2:common_types.Coordinate):
        self.base_geometry = LineString([pt1,pt2])
        
    def find_fraction_point(self, fraction:float):
        return self.endpt_lu + (self.endpt_rd-self.endpt_lu) * fraction
    
    def rotated_copy(self,pivot, angle):
        cpy = copy.deepcopy(self)
        cpy.rotate(pivot,angle)
        return cpy
        
    def rotate(self,pivot,angle):
        """rotate the linesegment counter-clockwise
        """
        new_pt1 = rotate_point(self.endpt_lu,pivot_point=pivot,theta=angle)
        new_pt2 = rotate_point(self.endpt_rd,pivot,angle)
        self.set_endpoints(new_pt1,new_pt2)

