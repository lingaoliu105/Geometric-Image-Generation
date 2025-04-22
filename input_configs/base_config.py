from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import os

@dataclass
class BasicAttributesDistribution:
    color_distribution: List[float]
    lightness_distribution: List[float]
    background_lightness_distribution: List[float]
    pattern_distribution: List[float]
    outline_distribution: List[float]
    shape_distribution: List[float]

@dataclass
class BaseConfig:
    layout: List[int]
    panel_configs: List["PanelConfig"]
    basic_attributes_distribution: BasicAttributesDistribution
    parent: Optional['BaseConfig'] = None
    
    def __getattr__(self, name: str) -> Any:
        """Support attribute inheritance from parent config"""
        if self.parent is not None and hasattr(self.parent, name):
            return getattr(self.parent, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def create_child(self) -> 'BaseConfig':
        """Create a child configuration that inherits from this one"""
        return self.__class__(
            layout=self.layout,
            panel_configs=self.panel_configs,
            basic_attributes_distribution=self.basic_attributes_distribution,
            parent=self
        )

    @classmethod
    def from_json(cls, json_path: str) -> 'BaseConfig':
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        # Convert basic_attributes_distribution dict to class instance
        basic_attrs = BasicAttributesDistribution(**data['basic_attributes_distribution'])
        
        return cls(
            layout=data['layout'],
            panel_configs=data['panel_configs'],
            basic_attributes_distribution=basic_attrs
        )
    
    def to_json(self, json_path: str) -> None:
        data = {
            'layout': self.layout,
            'panel_configs': self.panel_configs,
            'basic_attributes_distribution': {
                'color_distribution': self.basic_attributes_distribution.color_distribution,
                'lightness_distribution': self.basic_attributes_distribution.lightness_distribution,
                'background_lightness_distribution': self.basic_attributes_distribution.background_lightness_distribution,
                'pattern_distribution': self.basic_attributes_distribution.pattern_distribution,
                'outline_distribution': self.basic_attributes_distribution.outline_distribution,
                'shape_distribution': self.basic_attributes_distribution.shape_distribution
            }
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    @classmethod
    def read_input_folder(cls, input_folder: str) -> Dict[str, Any]:
        """Read all JSON files from input folder and merge them into a single dictionary"""
        merged_data = {}
        input_path = Path(input_folder)
        
        if not input_path.exists() or not input_path.is_dir():
            raise ValueError(f"Input folder {input_folder} does not exist or is not a directory")
        
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = Path(root) / file
                    with open(file_path, 'r') as f:
                        try:
                            data = json.load(f)
                            if isinstance(data, dict):
                                merged_data.update(data)
                        except json.JSONDecodeError:
                            print(f"Warning: Could not parse JSON file {file_path}")
        
        return merged_data
    
    @classmethod
    def merge_and_save_configs(cls, input_folder: str, output_file: str) -> None:
        """Read all configs from input folder, merge them and save to a single JSON file"""
        merged_data = cls.read_input_folder(input_folder)
        
        # Ensure the output directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(merged_data, f, indent=4)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """递归地从字典数据创建BaseConfig及其嵌套对象"""
        basic_attrs = BasicAttributesDistribution(**data['basic_attributes_distribution'])
        from .panel_config import PanelConfig
        panel_configs = []
        for pc in data.get('panel_configs', []):
            if isinstance(pc, dict):
                panel_configs.append(PanelConfig.from_dict(pc))
            else:
                panel_configs.append(pc)
        return cls(
            layout=data['layout'],
            panel_configs=panel_configs,
            basic_attributes_distribution=basic_attrs
        )

    def to_dict(self) -> Dict[str, Any]:
        """递归地将BaseConfig及其嵌套对象转为字典"""
        return {
            'layout': self.layout,
            'panel_configs': [pc.to_dict() if hasattr(pc, 'to_dict') else pc for pc in self.panel_configs],
            'basic_attributes_distribution': {
                'color_distribution': self.basic_attributes_distribution.color_distribution,
                'lightness_distribution': self.basic_attributes_distribution.lightness_distribution,
                'background_lightness_distribution': self.basic_attributes_distribution.background_lightness_distribution,
                'pattern_distribution': self.basic_attributes_distribution.pattern_distribution,
                'outline_distribution': self.basic_attributes_distribution.outline_distribution,
                'shape_distribution': self.basic_attributes_distribution.shape_distribution
            }
        }