import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from input_configs.generator_configs import ChainingImageConfig, EnclosingImageConfig, ParallelImageConfig, RadialImageConfig, RandomImageConfig, SimpleImageConfig, BorderImageConfig
from pydantic import BaseModel, Field, field_validator, model_validator
import jsonref

class ConfigBaseModel(BaseModel):
    color_distribution: Optional[List[float]] = None
    lightness_distribution: Optional[List[float]] = None
    background_lightness_distribution: Optional[List[float]] = None
    pattern_distribution: Optional[List[float]] = None
    outline_distribution: Optional[List[float]] = None
    shape_distribution: Optional[List[float]] = None
    
    model_config = {
        "extra":"allow"
    }


class BaseConfigModel(ConfigBaseModel):
    layout: List[int]
    canvas_width: float
    canvas_height: float
    panel_configs: List["NestedConfigModel"]

    @model_validator(mode="after")
    def set_parents(self) -> "BaseConfigModel":
        for child in self.panel_configs:
            child.parent = self
        return self


class NestedConfigModel(ConfigBaseModel): # a common superclass of both PanelConfig and ElementConfig, since they share mostly same structure
    parent: ConfigBaseModel = Field(default=None, exclude=True)
    composition_type:Dict[str,float]
    simple_image_config:Optional["SimpleImageConfigModel"] = None
    chaining_image_config:Optional["ChainingImageConfigModel"] = None
    enclosing_image_config:Optional["EnclosingImageConfigModel"] = None
    parallel_image_config:Optional["ParallelImageConfigModel"] = None
    radial_image_config:Optional["RadialImageConfigModel"] = None
    random_image_config:Optional["RandomImageConfigModel"] = None
    border_image_config:Optional["BorderImageConfigModel"] = None
    def model_post_init(self, __context: Any) -> None:
        for img_config_name in ["chaining_image_config", "enclosing_image_config", "parallel_image_config", "radial_image_config", "random_image_config", "border_image_config"]: # without simple_image_config
            if getattr(self, img_config_name) is not None:
                img_cfg = getattr(self, img_config_name)
                for sub_element in img_cfg.sub_elements:
                    sub_element.parent = self

class GeneratorConfigModel(BaseModel):
    pass

class GeneratorConfigModelWithSubElements(GeneratorConfigModel):
    sub_elements:List[NestedConfigModel]

class SimpleImageConfigModel(GeneratorConfigModel):
    aspect_ratio: Optional[Dict[str, float] ] = None

class ChainingImageConfigModel(GeneratorConfigModelWithSubElements):
    element_num: int
    chain_shape: str
    draw_chain: bool
    chain_level: str
    interval: float
    rotation: float
class EnclosingImageConfigModel(GeneratorConfigModelWithSubElements):
    enclose_level: int

class ParallelImageConfigModel(GeneratorConfigModelWithSubElements):
    pass

class RadialImageConfigModel(GeneratorConfigModelWithSubElements):
    pass

class RandomImageConfigModel(GeneratorConfigModelWithSubElements):
    centralization: float
    element_num: int

class BorderImageConfigModel(GeneratorConfigModelWithSubElements):
    pass
