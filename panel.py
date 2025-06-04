import random
from typing import List

import numpy as np

import img_params
import util
from entities.entity import Relationship
from entities.simple_shape import SimpleShape
from entities.touching_point import TouchingPoint
from entities.visible_shape import VisibleShape
from generation_config import GenerationConfig


class Panel:
    def __init__(
        self,
        top_left: list[float],
        bottom_right: list[float],
        shapes: List[VisibleShape],
        joints: List[Relationship],
        color=None,
        lightness=None,
    ) -> None:
        self.top_left = top_left
        self.bottom_right = bottom_right
        top_left = np.array(top_left)
        bottom_right = np.array(bottom_right)
        self.shapes = shapes
        self.joints = joints
        center = (top_left + bottom_right) / 2
        radius = np.linalg.norm(center - top_left)
        color = (
            color
            if color is not None
            else util.choose_color(GenerationConfig.color_distribution)
        )

        lightness = (
            lightness
            if lightness is not None
            else util.choose_item_by_distribution(img_params.Lightness,GenerationConfig.background_lightness_distribution)
        )
        if GenerationConfig.color_mode == "mono":
            color = img_params.Color.black
        self.background = SimpleShape(
            position=center,
            size=radius,
            shape=img_params.Shape.square,
            color=color,
            lightness=lightness,
            pattern=img_params.Pattern.blank,
            outline=img_params.Outline.solid,
            outline_color=img_params.OutlineColor.outlineBlack,
            outline_lightness=img_params.OutlineLightness.outlineLightness100,
            outline_thickness=img_params.OutlineThickness.thick,
            rotation=img_params.Angle.deg0,
        )
