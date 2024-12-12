'''
This file defines the abstract class for the entities' hierachy
'''
import copy
from enum import Enum
import json
import random
from typing import Optional

import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry

from generation_config import GenerationConfig
import img_params
import uid_service

from abc import ABC, abstractmethod
from shapely.affinity import translate

from util import *
import util


class Entity(ABC):

    def __init__(self) -> None:
        self.uid = uid_service.get_new_entity_uid()
    def to_dict(self):
        dict = {attr_name: getattr(self, attr_name) for attr_name in self.serialized_fields}
        for key in dict:
            value = dict[key]
            try:
                json.dumps(value)
            except TypeError:
                if isinstance(value, np.ndarray):
                    value = value.tolist()
                elif isinstance(value, Enum):
                    value = value.name
                elif isinstance(value, BaseGeometry):
                    value = shapely.geometry.mapping(value)
                elif isinstance(value,Entity): # when attribute is SimpleShape instance, only record down the id
                    value = value.uid
                dict[key] = value

        return dict

    def to_tikz(self)->str:
        return self.tikz_converter.convert(self)

    def copy(self):
        return copy.deepcopy(self)

    @property
    def copy(self):
        return copy.deepcopy(self)


class Relationship(Entity,ABC):
    pass

class VisibleShape(Entity,ABC):

    def __init__(
        self,
        tikz_converter,
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
    ) -> None:
        super().__init__()
        self._base_geometry:BaseGeometry = None
        assert tikz_converter is not None
        self.tikz_converter  = tikz_converter
        self.color = (
            color if color is not None else util.choose_color(GenerationConfig.color_distribution)
        )
        
        self.lightness = (
            lightness
            if lightness is not None
            else random.choice(list(img_params.Lightness))
        )

    @abstractmethod
    def expand(self,ratio):
        pass

    @abstractmethod
    def expand_fixed(self,length):
        pass

    def overlaps(self,other:"VisibleShape"):
        return self._base_geometry.overlaps(other.base_geometry)

    @property
    @abstractmethod
    def center(self):
        pass

    def to_tikz(self)->str:
        return self.tikz_converter.convert(self)

    @property
    def base_geometry(self):
        return self._base_geometry
    
    def shift(self,offset:common_types.Coordinate):
        self._base_geometry = translate(self._base_geometry,xoff=offset[0],yoff=offset[1])

class ClosedShape(VisibleShape):

    def __init__(
        self,
        tikz_converter,
        pattern: Optional[img_params.Pattern] = None,
        outline=None,
        outline_lightness=None,
        pattern_color=None,
        pattern_lightness=None,
        outline_color=None,
        outline_thickness=None,
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
    ) -> None:
        super().__init__(tikz_converter,color=color,lightness=lightness)
        self.pattern = (
            pattern if pattern is not None else random.choice(list(img_params.Pattern))
        )
        self.pattern_lightness = (
            pattern_lightness
            if pattern_lightness is not None
            else choose_param_with_beta(0.3, img_params.Lightness)
        )
        self.pattern_color = (
            pattern_color
            if pattern_color is not None
            else random.choice(list(img_params.PattenColor))
        )
        self.outline = (
            outline if outline is not None else random.choice(list(img_params.Outline))
        )
        self.outline_color = (
            outline_color
            if outline_color is not None
            else self.get_available_outline_color()
        )
        self.outline_thickness = (
            outline_thickness
            if outline_thickness is not None
            else random.choice(list(img_params.OutlineThickness))
        )
        self.outline_lightness = (
            outline_lightness
            if outline_lightness is not None
            else choose_param_with_beta(0.8, img_params.OutlineLightness)
        )

    def get_available_outline_color(self):
        """find available color for outline when inner color is determined, such that outline color and inner color differ

        Returns:
            _type_: _description_
        """
        available_outline_colors = list(img_params.OutlineColor)
        if self.color != None:
            for color_item in available_outline_colors:
                if color_item.name.lower().endswith(self.color.name.lower()):
                    available_outline_colors.remove(color_item)

        return random.choice(available_outline_colors)

class OpenShape(VisibleShape):
    pass
