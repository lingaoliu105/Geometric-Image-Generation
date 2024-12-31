import copy
from enum import Enum
import json
import random
from typing import Optional

import numpy as np
import shapely
from shapely.geometry.base import BaseGeometry

from entities.visible_shape import VisibleShape
from generation_config import GenerationConfig
import img_params
import uid_service

from abc import ABC, abstractmethod
from shapely.affinity import translate, rotate

from util import *
import util


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
        super().__init__(tikz_converter, color=color, lightness=lightness)
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