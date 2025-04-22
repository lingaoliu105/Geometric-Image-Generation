from dataclasses import dataclass, field
from typing import Dict, Optional, Union, Any, List
from .base_config import BaseConfig

@dataclass
class ElementConfig(BaseConfig):
    """Configuration for an element in the panel"""
    element_type: str
    attributes: Dict[str, Any]
    parent: Optional[BaseConfig] = None
    children: List['ElementConfig'] = field(default_factory=list)
    
    @classmethod
    def from_json(cls, json_path: str) -> 'ElementConfig':
        """Create an ElementConfig instance from a JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            element_type=data['element_type'],
            attributes=data['attributes']
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ElementConfig':
        return cls(
            element_type=data['element_type'],
            attributes=data['attributes']
        )

    def to_dict(self) -> dict:
        return {
            'element_type': self.element_type,
            'attributes': self.attributes
        }
    
    def to_json(self, json_path: str) -> None:
        """Save the ElementConfig instance to a JSON file"""
        data = {
            'element_type': self.element_type,
            'attributes': self.attributes
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)