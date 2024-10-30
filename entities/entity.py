'''
This file defines the abstract class for the entities' hierachy
'''
import copy
from enum import Enum
import json

import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry

import uid_service

from abc import ABC, abstractmethod


class Entity(ABC):

    def __init__(self,tikz_converter) -> None:
        self.uid = uid_service.get_new_entity_uid()
        assert tikz_converter is not None
        self.tikz_converter  = tikz_converter
    def to_dict(self):
        dict = {slot: getattr(self, slot) for slot in self.__slots__}
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
    @abstractmethod
    def expand(self,ratio):
        pass
    
    @abstractmethod
    def expand_fixed(self,length):
        """change the shape by a fixed length (delta of size)
        if the shape is closed, the size (radius) changes by length
        if the shape is linesegment, the half-length changes by length, total length changes by 2*length
        length can be positive (expand) or negative (shrink)

        Args:
            length (_type_): _description_
        """
        pass

class ClosedShape(VisibleShape):
    pass

class OpenShape(VisibleShape):
    pass
