from dataclasses import dataclass, field, fields, asdict, is_dataclass
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
from .config_serialization_mixin import ConfigSerializationMixin # Import the mixin

@dataclass
class PanelConfig(ConfigSerializationMixin): # Inherit from the mixin
    """Configuration for a panel in the image"""
    panel_id: int
    # Optional for basic_attributes_distribution and composition_type, to be consistent with ElementConfig and from_dict logic
    basic_attributes_distribution: Optional[BasicAttributesDistribution] = None
    composition_type: Optional[Dict[str, float]] = None        

    simple_image_config: Optional["SimpleImageConfig"] = None
    chaining_image_config: Optional["ChainingImageConfig"] = None
    enclosing_image_config: Optional["EnclosingImageConfig"] = None
    parallel_image_config: Optional["ParallelImageConfig"] = None
    radial_image_config: Optional["RadialImageConfig"] = None

    @classmethod
    def _get_generator_config_field_names(cls) -> List[str]:
        return [
            "simple_image_config",
            "chaining_image_config",
            "enclosing_image_config",
            "parallel_image_config",
            "radial_image_config",
        ]

    @classmethod
    def _preprocess_data_for_from_dict(cls, data: Dict[str, Any], curr_path: Optional[Path] = None) -> Dict[str, Any]:
        processed_data = super()._preprocess_data_for_from_dict(data, curr_path) # Call base for generator configs

        # Handle BasicAttributesDistribution instantiation
        if 'basic_attributes_distribution' in processed_data and \
           isinstance(processed_data['basic_attributes_distribution'], dict):
            processed_data['basic_attributes_distribution'] = BasicAttributesDistribution(**processed_data['basic_attributes_distribution'])
        elif 'basic_attributes_distribution' not in processed_data and 'basic_attributes_distribution' in cls.__annotations__:
             processed_data['basic_attributes_distribution'] = None # Explicitly set to None if not in data
        
        # composition_type is a Dict, should be handled by default dataclass_json or from_dict in mixin if simple
        # No specific processing needed here unless it was a complex object string reference like generators
        # If 'composition_type' is not in data, it will use the default_factory or default value if defined.
        # If we want to ensure it's None if absent (and no default_factory), we can add:
        # elif 'composition_type' not in processed_data and 'composition_type' in cls.__annotations__:
        #      processed_data['composition_type'] = None

        return processed_data

    def to_dict(self) -> Dict[str, Any]:
        """Custom to_dict to handle nested generator configs correctly."""
        data = {}
        generator_field_names = self._get_generator_config_field_names()

        for f_info in fields(self):
            field_name = f_info.name
            # No 'parent' field in PanelConfig to skip, but good practice if it were added.
            # if field_name == 'parent': 
            #     continue
            
            field_value = getattr(self, field_name)

            if field_value is None:
                data[field_name] = None
            elif field_name in generator_field_names:
                # These are instances of classes inheriting from BaseGeneratorConfig
                if hasattr(field_value, 'to_dict') and callable(getattr(field_value, 'to_dict')):
                    data[field_name] = field_value.to_dict()
                else: 
                    data[field_name] = asdict(field_value) if is_dataclass(field_value) else field_value
            elif isinstance(field_value, BasicAttributesDistribution):
                data[field_name] = field_value.to_dict()
            elif is_dataclass(field_value):
                # For other potential nested dataclasses (e.g. if ElementConfig was directly a field)
                # This case needs to be careful to call their custom to_dict if they have one.
                if hasattr(field_value, 'to_dict') and callable(getattr(field_value, 'to_dict')):
                    data[field_name] = field_value.to_dict()
                else:
                    data[field_name] = asdict(field_value)
            else:
                # This covers simple types like dict, list, str, int, float, bool
                data[field_name] = field_value
        
        return data

    def _set_child_parent_references(self) -> None:
        """Sets the parent reference for child ElementConfigs and recursively calls this method on them."""
        # PanelConfig owns GeneratorConfigs, which in turn own sub_elements (ElementConfigs)
        for gen_cfg_field_name in self._get_generator_config_field_names():
            generator_config = getattr(self, gen_cfg_field_name, None)
            if generator_config and hasattr(generator_config, 'sub_elements'):
                for sub_element_cfg in generator_config.sub_elements:
                    if isinstance(sub_element_cfg, ElementConfig):
                        sub_element_cfg.parent = self # `self` is the current PanelConfig instance
                        # Recursively set parent references for children of this sub_element
                        sub_element_cfg._set_child_parent_references()
