from dataclasses import dataclass, field, fields, asdict, is_dataclass
from typing import List, Dict, Any, Optional, Union
import json
from pathlib import Path
import os

from .basic_attributes_distribution import BasicAttributesDistribution
from .panel_config import PanelConfig
from .config_serialization_mixin import ConfigSerializationMixin



@dataclass
class BaseConfig(ConfigSerializationMixin):
    layout: List[int]
     
    panel_configs: List[PanelConfig]
    basic_attributes_distribution: BasicAttributesDistribution

    @classmethod
    def _preprocess_data_for_from_dict(cls, data: Dict[str, Any], curr_path: Optional[Path] = None) -> Dict[str, Any]:
        # No call to super()._preprocess_data_for_from_dict as BaseConfig has no generator configs itself
        # and handles its nested objects (PanelConfig, BasicAttributesDistribution) uniquely.
        processed_data = data.copy()

        # 1. Handle BasicAttributesDistribution
        if 'basic_attributes_distribution' in processed_data and \
           isinstance(processed_data['basic_attributes_distribution'], dict):
            processed_data['basic_attributes_distribution'] = BasicAttributesDistribution(**processed_data['basic_attributes_distribution'])
        # If it's already an instance (e.g. programmatic construction), or not a dict, 
        # it might raise an error later or be an invalid type, but this part only handles dict conversion.
        # Assuming basic_attributes_distribution is a required field as per original dataclass definition.

        # 2. Handle panel_configs - this is the complex part
        if 'panel_configs' in processed_data and isinstance(processed_data['panel_configs'], list):
            loaded_panel_configs = []
            for pc_item in processed_data['panel_configs']:
                if isinstance(pc_item, str): # It's a path to a JSON file
                    if curr_path is None:
                        raise ValueError("curr_path must be provided to resolve panel_config file paths.")
                    panel_json_path = curr_path / pc_item
                    try:
                        # PanelConfig now uses the mixin, so PanelConfig.from_json is available
                        panel_config_obj = PanelConfig.from_json(str(panel_json_path))
                    except FileNotFoundError:
                        # Attempt to resolve relative to the original BaseConfig json_path's parent if curr_path failed
                        # This case might be redundant if curr_path is always the BaseConfig's dir
                        # However, if curr_path could be something else, this provides a fallback.
                        # For now, let's assume curr_path is correctly the BaseConfig dir.
                        raise FileNotFoundError(f"PanelConfig JSON file not found: {panel_json_path} (referenced in BaseConfig)")
                elif isinstance(pc_item, dict): # It's an inline dictionary
                    # PanelConfig.from_dict takes curr_path, which for inline panel configs within BaseConfig,
                    # should still be the directory of the BaseConfig itself, for resolving any nested paths within that panel_dict.
                    panel_config_obj = PanelConfig.from_dict(pc_item, curr_path=curr_path)
                else:
                    raise TypeError(f"Invalid item in panel_configs: expected str (path) or dict, got {type(pc_item)}")
                loaded_panel_configs.append(panel_config_obj)
            processed_data['panel_configs'] = loaded_panel_configs
        elif 'panel_configs' not in processed_data:
             raise ValueError("'panel_configs' is a required field for BaseConfig.")
        # If panel_configs is present but not a list, it will likely fail at dataclass instantiation. 

        # 3. layout is a List[int], should be directly usable if present in data.
        # No special processing needed here for layout itself.
        if 'layout' not in processed_data:
            raise ValueError("'layout' is a required field for BaseConfig.")

        return processed_data

    def _postprocess_data_for_to_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # No call to super()._postprocess_data_for_to_dict as BaseConfig has no generator configs itself.
        processed_data = data.copy() # data is from asdict(self)

        # 1. BasicAttributesDistribution is a dataclass, asdict handles it.
        #    No change needed unless custom dict structure is required.
        #    processed_data['basic_attributes_distribution'] = asdict(self.basic_attributes_distribution)

        # 2. panel_configs: list of PanelConfig objects. Need to call to_dict() on each.
        if 'panel_configs' in processed_data and isinstance(self.panel_configs, list):
            processed_data['panel_configs'] = [pc.to_dict() for pc in self.panel_configs]
        
        # 3. layout is List[int], asdict handles it.
        
        return processed_data

    def to_dict(self) -> Dict[str, Any]:
        """Custom to_dict to handle nested PanelConfig and BasicAttributesDistribution correctly."""
        data = {}
        for f_info in fields(self):
            field_name = f_info.name
            field_value = getattr(self, field_name)

            if field_value is None:
                data[field_name] = None
            elif field_name == 'panel_configs':
                # Ensure this is a list and elements have to_dict (which PanelConfig now does)
                if isinstance(field_value, list):
                    data[field_name] = [pc.to_dict() for pc in field_value if hasattr(pc, 'to_dict')]
                else:
                    data[field_name] = [] # Or handle error as appropriate
            elif isinstance(field_value, BasicAttributesDistribution):
                data[field_name] = field_value.to_dict()
            elif is_dataclass(field_value):
                # For any other dataclass fields (though none are expected currently in BaseConfig)
                # This should ideally call a custom to_dict if available
                if hasattr(field_value, 'to_dict') and callable(getattr(field_value, 'to_dict')):
                    data[field_name] = field_value.to_dict()
                else:
                    data[field_name] = asdict(field_value)
            else:
                # This covers simple types like list, dict, str, int, float, bool (e.g., self.layout)
                data[field_name] = field_value
        return data

    def get_hierarchy(self, base_path: Optional[Path] = None) -> Dict[str, Any]:
        """Recursively build a dictionary representing the configuration hierarchy."""
        panel_hierarchies = []
        for pc in self.panel_configs:
            # pc.to_dict() now comes from the Mixin and should be correct
            panel_data = pc.to_dict() 
            panel_hierarchies.append({
                f"panel_{pc.panel_id}": {
                    "type": pc.__class__.__name__,
                    **panel_data
                }
            })

        return {
            "type": self.__class__.__name__,
            "layout": self.layout,
            "panel_configs": panel_hierarchies,
            # self.basic_attributes_distribution is a dataclass, asdict is fine for hierarchy too.
            "basic_attributes_distribution": self.basic_attributes_distribution.to_dict()
        }

    def save_hierarchy_to_json(self, json_path: str, base_path: Optional[Path] = None) -> None:
        """Generate the hierarchy and save it to a JSON file."""
        hierarchy_data = self.get_hierarchy(base_path=base_path)
        output_path = Path(json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(hierarchy_data, f, indent=4)

    # Old from_json, to_dict, save_to_json are removed and functionality replaced by Mixin + hooks.
    # Ensure the actual methods below this comment (if any) are deleted.
    # For example, the old to_dict and save_to_json that might have been here:
    # def to_dict(self) -> Dict[str, Any]: ...
    # def save_to_json(self, json_path: str) -> None: ...
