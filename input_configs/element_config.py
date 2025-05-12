from dataclasses import dataclass, field, fields, asdict
from typing import Dict, Optional, Union, Any, List
import json
from pathlib import Path

from input_configs.basic_attributes_distribution import BasicAttributesDistribution
@dataclass
class ElementConfig:
    """Configuration for an element in the panel"""
    basic_attributes_distribution:BasicAttributesDistribution = field(default=None)
    composition_type:Dict[str,float] = field(default_factory=lambda:{"simple":1.0})

    from input_configs.generator_configs import BaseGeneratorConfig, ChainingImageConfig, EnclosingImageConfig, ParallelImageConfig, RadialImageConfig, SimpleImageConfig
    simple_image_config: Optional["SimpleImageConfig"] = None
    chaining_image_config: Optional["ChainingImageConfig"] = None
    enclosing_image_config: Optional["EnclosingImageConfig"] = None
    parallel_image_config: Optional["ParallelImageConfig"] = None
    radial_image_config: Optional["RadialImageConfig"] = None
    @classmethod
    def from_json(cls, json_path: str) -> 'ElementConfig':
        """Create an ElementConfig instance from a JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)

        return cls.from_dict(data,curr_path=Path(json_path))

    @classmethod
    def from_dict(cls, data: dict, curr_path:Path) -> 'ElementConfig':
        processed_data = data.copy() # Work on a copy

        # Convert basic_attributes_distribution dict to class instance if present
        if 'basic_attributes_distribution' in processed_data and \
           isinstance(processed_data['basic_attributes_distribution'], dict):
            processed_data['basic_attributes_distribution'] = BasicAttributesDistribution(**processed_data['basic_attributes_distribution'])

        generator_config_fields = [
            "simple_image_config",
            "chaining_image_config",
            "enclosing_image_config",
            "parallel_image_config",
            "radial_image_config",
        ] # generator configs that are  complex and have to be explicitly created and attached

        # Prepare init_args, ensuring only defined fields are passed to constructor
        # This avoids passing unexpected keys if 'data' contains more than ElementConfig fields.
        init_args = {}
        for f in fields(cls): # Iterate over dataclass fields
            if f.name in processed_data:
                if f.name in generator_config_fields:
                    from input_configs.generator_configs import BaseGeneratorConfig

                    init_args[f.name] = BaseGeneratorConfig.from_dict(processed_data[f.name],generator_config_type_name=f.name,curr_path=curr_path.parent)
                init_args[f.name] = processed_data[f.name]

        instance = cls(**init_args)
        return instance

    def to_dict(self) -> dict:
        """将 ElementConfig 实例转换为字典。"""
        return asdict(self)

    def to_json(self, json_path: str) -> None:
        """将 ElementConfig 实例转换为 JSON 文件。"""
        data = self.to_dict()
        output_path = Path(json_path)
        # Ensure the directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
