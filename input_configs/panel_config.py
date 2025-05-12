from dataclasses import dataclass, field, fields, asdict
from typing import Dict, Optional, Union, Any, List
import json
from pathlib import Path

from input_configs.basic_attributes_distribution import BasicAttributesDistribution

# Removed incorrect import: from .distribution_config import BasicAttributesDistribution
from .element_config import ElementConfig # Added import
from .generator_configs import (
    BaseGeneratorConfig,
    SimpleImageConfig,
    ChainingImageConfig,
    EnclosingImageConfig,
    ParallelImageConfig,
    RadialImageConfig
)

@dataclass
class PanelConfig:
    """Configuration for a panel in the image"""
    panel_id:int
    basic_attributes_distribution: Optional["BasicAttributesDistribution"] = None
    composition_type: Optional[Dict[str, float]] = None        

    simple_image_config: Optional["SimpleImageConfig"] = None
    chaining_image_config: Optional["ChainingImageConfig"] = None
    enclosing_image_config: Optional["EnclosingImageConfig"] = None
    parallel_image_config: Optional["ParallelImageConfig"] = None
    radial_image_config: Optional["RadialImageConfig"] = None
    @classmethod
    def from_dict(cls, data, curr_path:Path):
        generator_config_fields = [
            "simple_image_config",
            "chaining_image_config",
            "enclosing_image_config",
            "parallel_image_config",
            "radial_image_config",
        ] # generator configs that are  complex and have to be explicitly created and attached
        for f in fields(cls):

            if f.name in data:
                if f.name in generator_config_fields:
                    generator_config_dict = data[f.name]
                    data[f.name] = BaseGeneratorConfig.from_dict(generator_config_dict,f.name, curr_path=curr_path)
                    
        instance = cls(**data)

        return instance
        
    def to_dict(self) -> Dict[str, Any]:
        """递归地将PanelConfig及其嵌套对象转为字典"""
        data = {}
        generator_config_field_names = [
            "simple_image_config",
            "chaining_image_config",
            "enclosing_image_config",
            "parallel_image_config",
            "radial_image_config",
        ]

        for f_info in fields(self): # Iterate through all fields of PanelConfig
            field_name = f_info.name
            field_value = getattr(self, field_name)

            if field_value is None:
                data[field_name] = None
            elif field_name in generator_config_field_names:
                # These are instances of classes inheriting from BaseGeneratorConfig
                # We need to call their to_dict method.
                data[field_name] = field_value.to_dict()
            elif isinstance(field_value, BasicAttributesDistribution):
                # BasicAttributesDistribution is a simple dataclass, asdict is fine.
                data[field_name] = asdict(field_value)
            else:
                # This covers panel_id (int), composition_type (Dict), and any other simple fields.
                data[field_name] = field_value
        return data
