from dataclasses import dataclass, field, asdict, fields
from typing import List, Dict, Optional, Union, Any
# Forward declaration to avoid circular import
from pathlib import Path

@dataclass
class BaseGeneratorConfig:
    """Base class for all generator configs with inheritance support"""
    sub_elements:List = field(default_factory=list)
    @staticmethod
    def from_dict(data,generator_config_type_name:str, curr_path:Path):
        init_args = {}

        cls_map = {
            "simple_image_config":SimpleImageConfig,
            "chaining_image_config":ChainingImageConfig,
            "enclosing_image_config":EnclosingImageConfig,
            "parallel_image_config":ParallelImageConfig,
            "radial_image_config":RadialImageConfig
        }
        cls = cls_map[generator_config_type_name]
        sub_data_list = []
        for f in fields(cls):

            if f.name in data:
                if f.name=="sub_elements":
                    sub_data_list = data[f.name]
                    continue
                init_args[f.name] = data[f.name]
        instance = cls(**init_args)

        for sub_data_path in sub_data_list:
            from .element_config import ElementConfig
            instance.sub_elements.append(ElementConfig.from_json(curr_path / sub_data_path))
        return instance

    def to_dict(self) -> Dict[str, Any]:
        """递归地将 BaseGeneratorConfig 及其嵌套对象（包括子元素）转换为字典。"""
        data = {} # Manual serialization
        for f_info in fields(self):
            field_name = f_info.name
            field_value = getattr(self, field_name)

            if field_name == "sub_elements":
                if field_value:
                    serialized_sub_elements = []
                    for el in field_value: # field_value is self.sub_elements
                        if hasattr(el, 'to_dict') and callable(getattr(el, 'to_dict')):
                            serialized_sub_elements.append(el.to_dict())
                        else:
                            # Fallback for unexpected types, though normally ElementConfig instances
                            serialized_sub_elements.append(el) 
                    data[field_name] = serialized_sub_elements
                else:
                    data[field_name] = [] # or None, depending on desired output for empty

            else:
                 # For all other fields (expected to be simple types like int, str, bool, dict, list of primitives)
                data[field_name] = field_value
        return data

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

@dataclass
class EnclosingImageConfig(BaseGeneratorConfig):
    """Configuration for EnclosingImageGenerator"""
    enclose_level: int = 2

@dataclass
class ParallelImageConfig(BaseGeneratorConfig):
    """Configuration for ParallelImageGenerator"""
    pass


@dataclass
class RadialImageConfig(BaseGeneratorConfig):
    """Configuration for RadialImageGenerator"""
    pass
    
@dataclass
class RandomImageConfig(BaseGeneratorConfig):
    """Configuration for RandomImageGenerator"""
    centralization: float = 0.2
    element_num: int = 4
    
@dataclass
class BorderImageConfig(BaseGeneratorConfig):
    """Configuration for BorderImageGenerator"""
    pass

