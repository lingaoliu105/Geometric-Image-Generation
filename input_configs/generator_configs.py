from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
from pathlib import Path
from .base_config import BasicAttributesDistribution # Import BasicAttributesDistribution

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
        
    def to_dict(self) -> Dict[str, Any]:
        """将配置对象转换为字典表示"""
        # 获取所有实例变量
        result = {}
        for key, value in self.__dict__.items():
            # 跳过parent属性，避免循环引用
            if key == 'parent':
                continue
                
            # 处理嵌套对象
            if hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            elif isinstance(value, BasicAttributesDistribution):
                # Manually serialize BasicAttributesDistribution
                result[key] = {
                    'color_distribution': value.color_distribution,
                    'lightness_distribution': value.lightness_distribution,
                    'background_lightness_distribution': value.background_lightness_distribution,
                    'pattern_distribution': value.pattern_distribution,
                    'outline_distribution': value.outline_distribution,
                    'shape_distribution': value.shape_distribution
                }
            # 处理列表类型，检查列表中的每个元素是否可序列化
            elif isinstance(value, list):
                result[key] = []
                for item in value:
                    if hasattr(item, 'to_dict'):
                        result[key].append(item.to_dict())
                    elif isinstance(item, BasicAttributesDistribution):
                        # Manually serialize BasicAttributesDistribution in lists
                        result[key].append({
                            'color_distribution': item.color_distribution,
                            'lightness_distribution': item.lightness_distribution,
                            'background_lightness_distribution': item.background_lightness_distribution,
                            'pattern_distribution': item.pattern_distribution,
                            'outline_distribution': item.outline_distribution,
                            'shape_distribution': item.shape_distribution
                        })
                    else:
                        result[key].append(item)
            # 处理字典类型，检查字典中的每个值是否可序列化
            elif isinstance(value, dict):
                result[key] = {}
                for k, v in value.items():
                    if hasattr(v, 'to_dict'):
                        result[key][k] = v.to_dict()
                    elif isinstance(v, BasicAttributesDistribution):
                         # Manually serialize BasicAttributesDistribution in dicts
                        result[key][k] = {
                            'color_distribution': v.color_distribution,
                            'lightness_distribution': v.lightness_distribution,
                            'background_lightness_distribution': v.background_lightness_distribution,
                            'pattern_distribution': v.pattern_distribution,
                            'outline_distribution': v.outline_distribution,
                            'shape_distribution': v.shape_distribution
                        }
                    else:
                        result[key][k] = v
            else:
                result[key] = value
                
        return result

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