import random
import numpy as np
from entity import Entity
from typing import Optional, Union

import generation_config
import img_params
from tikz_converters import LineSegmentConverter
from uid_service import get_new_entity_uid


class LineSegment(Entity):
    direct_categories = [
        "color",
        "lightness",
    ]  # attributes that can be directly interpreted as categories in dataset annotations

    __slots__ = [
        "uid",
        "endpt_lu",  # the coordinate of the left, upper endpoint (compare left-right prior to up-down, i.e up-down only makes a difference when 2 endpoints are vertically aligned)
        "endpt_rd",  # the coordinate of the right, lower endpoint
        "base_geometry",
    ] + direct_categories

    def __init__(
        self,
        lu: Optional[Union[np.ndarray, tuple, list]] = None,
        rd: Optional[Union[np.ndarray, tuple, list]] = None,
        color: Optional[img_params.Color] = None,
        lightness: Optional[img_params.Lightness] = None,
    ) -> None:
        super().__init__(tikz_converter=LineSegmentConverter())
        if lu is None and rd is None:
            # if neither points is specified, choose both points randomly
            a, b, c, d = [
                random.uniform(
                    generation_config.GenerationConfig.left_canvas_bound,
                    generation_config.GenerationConfig.right_canvas_bound,
                )
                for _ in range(2)
            ] + [
                random.uniform(
                    generation_config.GenerationConfig.lower_canvas_bound,
                    generation_config.GenerationConfig.upper_canvas_bound,
                )
                for _ in range(2)
            ]
            l, r, u, d = min(a, b), max(a, b), min(c, d), max(c, d)
            self.endpt_lu = np.array([l, u])
            self.endpt_rd = np.array([r, d])
        elif lu is None:
            self.endpt_rd = np.array(rd)
            l = random.uniform(
                generation_config.GenerationConfig.left_canvas_bound, self.endpt_rd[0]
            )
            u = random.uniform(
                random.uniform(
                    generation_config.GenerationConfig.lower_canvas_bound,
                    generation_config.GenerationConfig.upper_canvas_bound,
                )
            )
            self.endpt_lu = np.array([l, u])
        elif rd is None:
            self.endpt_lu = lu
            r = random.uniform(
                self.endpt_lu[0], generation_config.GenerationConfig.right_canvas_bound
            )
            d = random.uniform(
                generation_config.GenerationConfig.lower_canvas_bound,
                generation_config.GenerationConfig.upper_canvas_bound,
            )
            self.endpt_rd = np.array([r, d])
        else:
            self.endpt_lu = np.array(lu)
            self.endpt_rd = np.array(rd)

        self.color = (
            color if color is not None else random.choice(list(img_params.Color))
        )
        self.lightness = (
            lightness
            if lightness is not None
            else random.choice(list(img_params.Lightness))
        )

    def shift(self,offset:np.ndarray):
        self.endpt_lu += offset
        self.endpt_rd+= offset
        

