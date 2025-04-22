from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

@dataclass
class BaseGeneratorConfig:
    """Base class for all generator configs with inheritance support"""
    parent: Optional['BaseGeneratorConfig'] = None
    
    def __getattr__(self, name: str) -> Any:
        """Support attribute inheritance from parent config"""
        if self.parent is not None and hasattr(self.parent, name):
            return getattr(self.parent, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def create_child(self) -> 'BaseGeneratorConfig':
        """Create a child configuration that inherits from this one"""
        return self.__class__(parent=self)

@dataclass
class SimpleImageConfig(BaseGeneratorConfig):
    """Configuration for SimpleImageGenerator"""
    shape_size: Dict[str, float] = field(default_factory=dict)  # min, max
    aspect_ratio: Dict[str, float] = field(default_factory=dict)  # min, max
    rotation_angles: List[float] = field(default_factory=list)
    polygon_generation: Dict[str, Union[List[float], str]] = field(default_factory=dict)

@dataclass
class ChainingImageConfig(BaseGeneratorConfig):
    """Configuration for ChainingImageGenerator"""
    element_num: int = 2
    chain_shape: str = "line"  # "line", "circle", "bezier"
    draw_chain: bool = False
    chain_level: str = "bottom"
    interval: float = 0.4
    rotation: float = 0
    control_point_distribution: Optional[Dict[str, Union[List[float], List[int]]]] = None
    elements: Optional[List[str]] = None  # paths to element configs

@dataclass
class EnclosingImageConfig(BaseGeneratorConfig):
    """Configuration for EnclosingImageGenerator"""
    outer_shape: str = "circle"
    inner_shape: str = "circle"
    scale_ratio: float = 0.8
    rotation: float = 0

@dataclass
class ParallelImageConfig(BaseGeneratorConfig):
    """Configuration for ParallelImageGenerator"""
    element_num: int = 2
    spacing: float = 0.5
    orientation: str = "horizontal"  # "horizontal", "vertical"
    elements: List[str] = field(default_factory=list)  # paths to element configs

@dataclass
class RadialImageConfig(BaseGeneratorConfig):
    """Configuration for RadialImageGenerator"""
    element_num: int = 4
    radius: float = 1.0
    rotation: float = 0
    elements: List[str] = field(default_factory=list)  # paths to element configs