from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import os

from input_configs.basic_attributes_distribution import BasicAttributesDistribution
from input_configs.panel_config import PanelConfig



@dataclass
class BaseConfig:
    layout: List[int]
    panel_configs: List["PanelConfig"]
    basic_attributes_distribution: BasicAttributesDistribution

    @classmethod
    def from_json(cls, json_path: str) -> 'BaseConfig':
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Convert basic_attributes_distribution dict to class instance
        basic_attrs = BasicAttributesDistribution(**data['basic_attributes_distribution'])
        
        # 处理panel_configs中的文件路径引用
        panel_configs = []
        json_dir = Path(json_path).parent
        
        for pc_dict in data['panel_configs']:
            

            panel_config = PanelConfig.from_dict(pc_dict, curr_path=Path(json_path).parent)
            panel_configs.append(panel_config)


        return cls(
            layout=data['layout'], 
            panel_configs=panel_configs,
            basic_attributes_distribution=basic_attrs
        )
    

    def get_hierarchy(self, base_path: Path = None) -> Dict[str, Any]:
        """Recursively build a dictionary representing the configuration hierarchy."""
        # For PanelConfig and its children, we'll use their to_dict representation for now.
        # A more detailed get_hierarchy could be added to PanelConfig later if needed.
        panel_hierarchies = []
        for pc in self.panel_configs:
            panel_data = pc.to_dict() # Assuming PanelConfig.to_dict() is implemented
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
            "basic_attributes_distribution": asdict(self.basic_attributes_distribution)
        }

    def save_hierarchy_to_json(self, json_path: str, base_path: Path = None) -> None:
        """Generate the hierarchy and save it to a JSON file."""
        hierarchy_data = self.get_hierarchy(base_path=base_path)
        # Ensure the directory exists
        output_path = Path(json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(hierarchy_data, f, indent=4)

    def save_to_json(self, json_path: str) -> None:
        """Save the BaseConfig instance to a JSON file using its to_dict representation."""
        data_to_save = self.to_dict()
        output_path = Path(json_path)
        # Ensure the directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data_to_save, f, indent=4)
    
        
    def to_dict(self) -> Dict[str, Any]:
        """递归地将BaseConfig及其嵌套对象转为字典"""
        return {
            'layout': self.layout,
            'panel_configs': [pc.to_dict() for pc in self.panel_configs],
            'basic_attributes_distribution': asdict(self.basic_attributes_distribution)
        }
