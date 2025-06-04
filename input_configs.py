from typing import Any, Dict, Iterator, List, Optional, TypeAlias, Union

from pydantic import BaseModel, Field, model_validator


class ConfigBaseModel(BaseModel):
    color_distribution: Optional[List[float]] = None
    lightness_distribution: Optional[List[float]] = None
    background_lightness_distribution: Optional[List[float]] = None
    pattern_distribution: Optional[List[float]] = None
    outline_distribution: Optional[List[float]] = None
    shape_distribution: Optional[List[float]] = None
    child_configs:Iterator["NestedConfigModel"] = Field(default=None, exclude=True)
    
    model_config = {
        "extra":"allow",
        "arbitrary_types_allowed":True
    }
    def iterate_next_child_to_access(self):
        try:
            self.next_child_to_access = next(self.child_configs)
            return self.next_child_to_access
        except StopIteration:
            return None


class BaseConfig(ConfigBaseModel):
    layout: List[int]
    canvas_width: float
    canvas_height: float
    panel_configs: List["NestedConfigModel"]
    opacity: float

    @model_validator(mode="after")
    def set_parents_for_children(self) -> "BaseConfig":
        for child in self.panel_configs:
            child.parent = self
        return self
    
    @model_validator(mode="after")
    def set_child_configs(self) -> "BaseConfig":
        self.child_configs = (panel_cfg for panel_cfg in self.panel_configs)
        return self


class NestedConfigModel(ConfigBaseModel): # a common superclass of both PanelConfig and ElementConfig, since they share mostly same structure
    parent: ConfigBaseModel = Field(default=None, exclude=True)
    composition_type:Dict[str,float]
    simple_image_config:Optional["SimpleImageConfig"] = None
    chaining_image_config:Optional["ChainingImageConfig"] = None
    enclosing_image_config:Optional["EnclosingImageConfig"] = None
    parallel_image_config:Optional["ParallelImageConfig"] = None
    radial_image_config:Optional["RadialImageConfig"] = None
    random_image_config:Optional["RandomImageConfig"] = None
    border_image_config:Optional["BorderImageConfig"] = None
    selected_generator_config:Optional["GeneratorConfigModelWithSubElements"] = Field(default=None, exclude=True)
    def model_post_init(self, __context: Any) -> None:
        for img_config_name in ["chaining_image_config", "enclosing_image_config", "parallel_image_config", "radial_image_config", "random_image_config", "border_image_config"]: # without simple_image_config
            if getattr(self, img_config_name) is not None:
                img_cfg = getattr(self, img_config_name)
                for sub_element in img_cfg.sub_elements:
                    sub_element.parent = self
                    
    
    def set_selected_generator_config(self, generator_config_name:str):
        if generator_config_name == "simple_image_config":
            raise ValueError("trying to set sub elements for simple image config, which is not allowed")
        self.selected_generator_config = {
            "chaining_image_config":self.chaining_image_config,
            "enclosing_image_config":self.enclosing_image_config,
            "parallel_image_config":self.parallel_image_config,
            "radial_image_config":self.radial_image_config,
            "random_image_config":self.random_image_config,
            "border_image_config":self.border_image_config,
        }[generator_config_name]
        self.child_configs = (cfg for cfg in self.selected_generator_config.sub_elements)   
    
    def iterate_next_child_to_access(self):
        try:
            return super().iterate_next_child_to_access() 
        except AttributeError:
            raise AttributeError("selected generator config is not set")
    

PanelConfig:TypeAlias =  NestedConfigModel
ElementConfig:TypeAlias = NestedConfigModel

class GeneratorConfigModel(BaseModel):
    pass

class GeneratorConfigModelWithSubElements(GeneratorConfigModel):
    sub_elements:List[NestedConfigModel]

class SimpleImageConfig(GeneratorConfigModel):
    aspect_ratio: Optional[Dict[str, float] ] = None

class ChainingImageConfig(GeneratorConfigModelWithSubElements):
    element_num: int
    chain_shape: str
    draw_chain: bool
    chain_level: str
    interval: float
    rotation: float
class EnclosingImageConfig(GeneratorConfigModelWithSubElements):
    enclose_level: int

class ParallelImageConfig(GeneratorConfigModelWithSubElements):
    pass

class RadialImageConfig(GeneratorConfigModelWithSubElements):
    pass

class RandomImageConfig(GeneratorConfigModelWithSubElements):
    centralization: float
    element_num: int

class BorderImageConfig(GeneratorConfigModelWithSubElements):
    pass
