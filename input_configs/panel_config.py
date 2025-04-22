from dataclasses import dataclass, field
from typing import Dict, Optional, Union, Any
from pathlib import Path
import json
from .base_config import BaseConfig
from .generator_configs import (
    SimpleImageConfig,
    ChainingImageConfig,
    EnclosingImageConfig,
    ParallelImageConfig,
    RadialImageConfig
)

@dataclass
class PanelConfig(BaseConfig):
    """Configuration for a panel in the image"""
    composition_type: Dict[str, float]  # probability distribution of composition types
    basic_attributes_distribution: Optional[Union[str, Dict]] = None
    parent: Optional['PanelConfig'] = None  # Override parent type to be more specific
    
    # Generator-specific configs - only one should be non-None based on composition_type
    simple_image_config: Optional[SimpleImageConfig] = None
    chaining_image_config: Optional[ChainingImageConfig] = None
    enclosing_image_config: Optional[EnclosingImageConfig] = None
    parallel_image_config: Optional[ParallelImageConfig] = None
    radial_image_config: Optional[RadialImageConfig] = None
    
    def create_child(self) -> 'PanelConfig':
        """Create a child configuration that inherits from this one"""
        return PanelConfig(
            composition_type=self.composition_type.copy(),
            basic_attributes_distribution=self.basic_attributes_distribution,
            parent=self
        )

    @classmethod
    def from_json(cls, json_path: str) -> 'PanelConfig':
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Load basic attributes distribution if it's a path
        basic_attrs = data.get('basic_attributes_distribution')
        if isinstance(basic_attrs, str):
            with open(basic_attrs, 'r') as f:
                basic_attrs = json.load(f)
        
        # Initialize generator config based on composition type
        generator_config = None
        if 'simple' in data['composition_type']:
            generator_config = SimpleImageConfig(**data.get('simple_image_config', {}))
        elif 'chaining' in data['composition_type']:
            generator_config = ChainingImageConfig(**data.get('chaining_image_config', {}))
        elif 'enclosing' in data['composition_type']:
            generator_config = EnclosingImageConfig(**data.get('enclosing_image_config', {}))
        elif 'parallel' in data['composition_type']:
            generator_config = ParallelImageConfig(**data.get('parallel_image_config', {}))
        elif 'radial' in data['composition_type']:
            generator_config = RadialImageConfig(**data.get('radial_image_config', {}))
        
        return cls(
            composition_type=data['composition_type'],
            basic_attributes_distribution=basic_attrs,
            simple_image_config=generator_config if isinstance(generator_config, SimpleImageConfig) else None,
            chaining_image_config=generator_config if isinstance(generator_config, ChainingImageConfig) else None,
            enclosing_image_config=generator_config if isinstance(generator_config, EnclosingImageConfig) else None,
            parallel_image_config=generator_config if isinstance(generator_config, ParallelImageConfig) else None,
            radial_image_config=generator_config if isinstance(generator_config, RadialImageConfig) else None
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PanelConfig':
        from .generator_configs import (
            SimpleImageConfig,
            ChainingImageConfig,
            EnclosingImageConfig,
            ParallelImageConfig,
            RadialImageConfig
        )
        basic_attrs = data.get('basic_attributes_distribution')
        parent = data.get('parent')
        # 递归处理parent
        if isinstance(parent, dict):
            parent = PanelConfig.from_dict(parent)
        # 递归处理生成器配置
        simple_cfg = data.get('simple_image_config')
        chaining_cfg = data.get('chaining_image_config')
        enclosing_cfg = data.get('enclosing_image_config')
        parallel_cfg = data.get('parallel_image_config')
        radial_cfg = data.get('radial_image_config')
        return cls(
            composition_type=data['composition_type'],
            basic_attributes_distribution=basic_attrs,
            parent=parent,
            simple_image_config=SimpleImageConfig(**simple_cfg) if simple_cfg else None,
            chaining_image_config=ChainingImageConfig(**chaining_cfg) if chaining_cfg else None,
            enclosing_image_config=EnclosingImageConfig(**enclosing_cfg) if enclosing_cfg else None,
            parallel_image_config=ParallelImageConfig(**parallel_cfg) if parallel_cfg else None,
            radial_image_config=RadialImageConfig(**radial_cfg) if radial_cfg else None
        )

    def to_dict(self) -> Dict[str, Any]:
        data = {
            'composition_type': self.composition_type,
            'basic_attributes_distribution': self.basic_attributes_distribution,
            'parent': self.parent.to_dict() if self.parent and hasattr(self.parent, 'to_dict') else None
        }
        if self.simple_image_config:
            data['simple_image_config'] = self.simple_image_config.__dict__
        if self.chaining_image_config:
            data['chaining_image_config'] = self.chaining_image_config.__dict__
        if self.enclosing_image_config:
            data['enclosing_image_config'] = self.enclosing_image_config.__dict__
        if self.parallel_image_config:
            data['parallel_image_config'] = self.parallel_image_config.__dict__
        if self.radial_image_config:
            data['radial_image_config'] = self.radial_image_config.__dict__
        return data
    
    def to_json(self, json_path: str) -> None:
        data = {
            'composition_type': self.composition_type,
            'basic_attributes_distribution': self.basic_attributes_distribution
        }
        
        # Add the active generator config
        if self.simple_image_config:
            data['simple_image_config'] = self.simple_image_config.__dict__
        elif self.chaining_image_config:
            data['chaining_image_config'] = self.chaining_image_config.__dict__
        elif self.enclosing_image_config:
            data['enclosing_image_config'] = self.enclosing_image_config.__dict__
        elif self.parallel_image_config:
            data['parallel_image_config'] = self.parallel_image_config.__dict__
        elif self.radial_image_config:
            data['radial_image_config'] = self.radial_image_config.__dict__
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)