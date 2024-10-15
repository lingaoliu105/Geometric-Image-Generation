from enum import Enum
import json

import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry


class Entity():


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
