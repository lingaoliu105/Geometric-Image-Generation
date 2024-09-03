from enum import Enum
import json

import numpy as np
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
                    value = value.value
                elif isinstance(value, BaseGeometry):
                    value = value.__geo_interface__
                elif isinstance(value,Entity): # when attribute is SimpleShape instance, only record down the id
                    value = value.uid
                dict[key] = value

        return dict
