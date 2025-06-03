from typing import Dict, List, Optional
from input_configs.generator_configs import ChainingImageConfig, EnclosingImageConfig, ParallelImageConfig, RadialImageConfig, RandomImageConfig, SimpleImageConfig, BorderImageConfig
from pydantic import BaseModel

class ConfigBaseModel(BaseModel):
    id:int
    color_distribution: List[float]
    lightness_distribution: List[float]
    background_lightness_distribution: List[float]
    pattern_distribution: List[float]
    outline_distribution: List[float]
    shape_distribution: List[float]
    
class BaseConfigModel(ConfigBaseModel):
    layout: List[int]
    canvas_width: float
    canvas_height: float
    panel_configs: List["NestedConfigModel"]
    

class NestedConfigModel(ConfigBaseModel): # a common superclass of both PanelConfig and ElementConfig, since they share mostly same structure
    parent: ConfigBaseModel
    composition_type:Dict[str,float]
    simple_image_config:Optional[SimpleImageConfig]
    chaining_image_config:Optional[ChainingImageConfig]
    enclosing_image_config:Optional[EnclosingImageConfig]
    parallel_image_config:Optional[ParallelImageConfig]
    radial_image_config:Optional[RadialImageConfig]
    random_image_config:Optional[RandomImageConfig]
    border_image_config:Optional[BorderImageConfig]
    parent: ConfigBaseModel
    

