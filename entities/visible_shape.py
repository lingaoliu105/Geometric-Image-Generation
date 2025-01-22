from enum import Enum
import json
import random
from typing import Optional, Union

import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry

from entities.entity import Entity
from generation_config import GenerationConfig
import img_params
import uid_service

from abc import ABC, abstractmethod
from shapely.affinity import translate, rotate, scale

from util import *
import util

class VisibleShape(Entity, ABC):

    def __init__(
        self,
        tikz_converter,
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
    ) -> None:
        super().__init__()
        self._base_geometry: BaseGeometry = None
        assert tikz_converter is not None
        self.tikz_converter = tikz_converter
        self.color = (
            color
            if color is not None
            else util.choose_color(GenerationConfig.color_distribution)
        )

        self.lightness = (
            lightness
            if lightness is not None
            else util.choose_item_by_distribution(img_params.Lightness,GenerationConfig.lightness_distribution)
        )
        if generation_config.GenerationConfig.color_mode == "mono":
            self.color = img_params.Color.black


    @abstractmethod
    def expand(self, ratio):
        pass

    @abstractmethod
    def expand_fixed(self, length):
        pass

    def overlaps(self, other: "VisibleShape"):
        return self._base_geometry.overlaps(other.base_geometry)

    @property
    @abstractmethod
    def center(self):
        pass

    def to_tikz(self) -> str:
        return self.tikz_converter.convert(self)

    @property
    def base_geometry(self):
        return self._base_geometry

    def shift(self, offset: common_types.Coordinate):
        self._base_geometry = translate(
            self._base_geometry, xoff=offset[0], yoff=offset[1]
        )

    def rotate(self, angle:Union[img_params.Angle,int], origin="center"):
        """
        Rotate the geometry by a specified angle around a given origin.

        Parameters:
        angle (float): The angle of rotation in degrees.
        origin (str or tuple): The point around which to rotate.
                             Options are 'center', 'centroid', or a tuple (x, y).
        """
        if not isinstance(origin,str):
            origin = tuple(origin)
        if isinstance(angle,img_params.Angle):
            angle = angle.value
        self._base_geometry = rotate(self._base_geometry, angle, origin)
        
    def scale(self,ratio,origin="center"):
        if not isinstance(origin,str):
            origin = tuple(origin)
        self._base_geometry = scale(self._base_geometry,xfact=ratio,yfact=ratio,origin=origin)

class OpenShape(VisibleShape):
    pass
