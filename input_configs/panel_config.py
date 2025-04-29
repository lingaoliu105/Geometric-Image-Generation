from dataclasses import dataclass, field
from typing import Dict, Optional, Union, Any, List
import json
from pathlib import Path
from .base_config import BaseConfig, BasicAttributesDistribution # Corrected import
# Removed incorrect import: from .distribution_config import BasicAttributesDistribution
from .element_config import ElementConfig # Added import
from .generator_configs import (
    SimpleImageConfig,
    ChainingImageConfig,
    EnclosingImageConfig,
    ParallelImageConfig,
    RadialImageConfig
)

# 不使用dataclass装饰器，而是手动实现__init__方法
class PanelConfig:
    """Configuration for a panel in the image"""
    
    def __init__(
        self,
        # 从BaseConfig继承的必需参数
        layout: List[int],
        # panel_configs: List["PanelConfig"], # Removed old panel_configs
        element_configs: List["ElementConfig"], # Added element_configs
        basic_attributes_distribution: BasicAttributesDistribution,
        # PanelConfig特有的必需参数
        composition_type: Dict[str, float] = None,  # probability distribution of composition types
        # 可选参数
        parent: Optional['PanelConfig'] = None,  # Override parent type to be more specific
        # Generator-specific configs
        simple_image_config: Optional[SimpleImageConfig] = None,
        chaining_image_config: Optional[ChainingImageConfig] = None,
        enclosing_image_config: Optional[EnclosingImageConfig] = None,
        parallel_image_config: Optional[ParallelImageConfig] = None,
        radial_image_config: Optional[RadialImageConfig] = None
    ):
        # 直接设置PanelConfig的属性
        self.layout = layout
        self.basic_attributes_distribution = basic_attributes_distribution
        self.parent = parent
        self.element_configs = element_configs # Added element_configs assignment
        self.composition_type = composition_type
        self.simple_image_config = simple_image_config
        self.chaining_image_config = chaining_image_config
        self.enclosing_image_config = enclosing_image_config
        self.parallel_image_config = parallel_image_config
        self.radial_image_config = radial_image_config
    
    def create_child(self) -> 'PanelConfig':
        """Create a child configuration based on this one"""
        # Note: Deep copy might be needed for mutable types like lists/dicts if modification is expected
        return PanelConfig(
            layout=self.layout, # Or deepcopy(self.layout)
            element_configs=self.element_configs, # Or deepcopy(self.element_configs)
            basic_attributes_distribution=self.basic_attributes_distribution, # Or deepcopy
            composition_type=self.composition_type.copy() if self.composition_type else None,
            parent=self, # Child's parent is the current instance
            simple_image_config=self.simple_image_config, # Or deepcopy
            chaining_image_config=self.chaining_image_config, # Or deepcopy
            enclosing_image_config=self.enclosing_image_config, # Or deepcopy
            parallel_image_config=self.parallel_image_config, # Or deepcopy
            radial_image_config=self.radial_image_config # Or deepcopy
        )

    @classmethod
    def from_json(cls, json_path: str) -> 'PanelConfig':
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Load basic attributes distribution if it's a path
        basic_attrs_data = data.get('basic_attributes_distribution')
        if isinstance(basic_attrs_data, str):
            # Assume path is relative to json_path's directory
            basic_attrs_path = Path(json_path).parent / basic_attrs_data
            if basic_attrs_path.exists():
                with open(basic_attrs_path, 'r') as f:
                    basic_attrs_dict = json.load(f)
                basic_attrs = BasicAttributesDistribution(**basic_attrs_dict)
            else:
                print(f"Warning: Basic attributes file not found: {basic_attrs_path}")
                basic_attrs = BasicAttributesDistribution() # Default or error handling
        elif isinstance(basic_attrs_data, dict):
             basic_attrs = BasicAttributesDistribution(**basic_attrs_data)
        else:
             basic_attrs = BasicAttributesDistribution() # Default or error handling

        # 处理 element_configs (assuming key might still be 'panel_configs' in JSON for compatibility or needs update)
        json_dir = Path(json_path).parent
        element_configs_data = data.get('panel_configs', []) # Use 'panel_configs' key for now
        element_configs = []
        for elem_data in element_configs_data:
            if isinstance(elem_data, str) and elem_data.endswith('.json'):
                file_path = json_dir / elem_data
                if file_path.exists():
                    try:
                        with open(file_path, 'r') as f:
                            config_data = json.load(f)
                        # Pass the directory of the element config file as base_dir
                        element_config = ElementConfig.from_dict(config_data, base_dir=str(file_path.parent))
                        element_configs.append(element_config)
                    except Exception as e:
                        print(f"Warning: Error loading element config {file_path}: {e}")
                        element_configs.append(elem_data) # Keep original reference on error
                else:
                    print(f"Warning: Referenced element config file not found: {file_path}")
                    element_configs.append(elem_data) # Keep original reference if not found
            elif isinstance(elem_data, dict):
                 # Assume dict represents an inline ElementConfig
                 try:
                     element_configs.append(ElementConfig.from_dict(elem_data, base_dir=str(json_dir)))
                 except Exception as e:
                     print(f"Warning: Error creating ElementConfig from dict: {e}")
                     element_configs.append(elem_data) # Keep original dict on error
            else:
                 # Keep other types as is (e.g., if already loaded objects)
                 element_configs.append(elem_data)

        # 处理chaining_image_config中的elements列表 (existing logic seems okay)
        chaining_cfg = data.get('chaining_image_config', {})
        if chaining_cfg and 'elements' in chaining_cfg:
            elements = []
            for elem in chaining_cfg['elements']:
                if isinstance(elem, str) and elem.endswith('.json'):
                    # 处理文件路径引用，尝试多种可能的路径
                    # 1. 相对于json文件目录的路径
                    file_path = json_dir / elem
                    
                    # 2. 如果是./element_configs/开头，尝试多种路径解析方式
                    if not file_path.exists() and './element_configs/' in elem:
                        elem_name = Path(elem).name
                        # 从element_config_1.json提取数字部分
                        if elem_name.startswith('element_config_') and elem_name.endswith('.json'):
                            num = elem_name[len('element_config_'):-len('.json')]
                            if num.isdigit():
                                # 尝试多种可能的路径
                                possible_paths = [
                                    # 使用element{num}.json格式在panel1目录下查找
                                    json_dir / 'panel1' / f"element{num}.json",
                                    # 直接在panel_configs目录下查找
                                    json_dir / f"element{num}.json",
                                    # 在panel1/element{num}目录下查找
                                    json_dir / 'panel1' / f"element{num}" / f"element{num}.json"
                                ]
                                
                                for alt_path in possible_paths:
                                    if alt_path.exists():
                                        file_path = alt_path
                                        break
                    
                    if file_path.exists():
                        try:
                            # 导入ElementConfig类
                            with open(file_path, 'r') as f:
                                elem_data = json.load(f)
                            # 加载element配置文件
                            element_config = ElementConfig.from_dict(elem_data)
                            elements.append(element_config)
                        except Exception as e:
                            print(f"Warning: Error loading element config {file_path}: {e}")
                            # 保留原始引用，以便后续处理
                            elements.append(elem)
                    else:
                        print(f"Warning: Referenced element config file not found: {file_path}")
                        # 保留原始引用，以便后续处理
                        elements.append(elem)
                else:
                    # 如果是字典或其他类型，直接添加
                    elements.append(elem)
            chaining_cfg['elements'] = elements
        
        # Initialize generator config based on composition type
        generator_config = None
        if 'simple' in data['composition_type']:
            generator_config = SimpleImageConfig(**data.get('simple_image_config', {}))
        elif 'chaining' in data['composition_type']:
            generator_config = ChainingImageConfig(**chaining_cfg)
        elif 'enclosing' in data['composition_type']:
            generator_config = EnclosingImageConfig(**data.get('enclosing_image_config', {}))
        elif 'parallel' in data['composition_type']:
            generator_config = ParallelImageConfig(**data.get('parallel_image_config', {}))
        elif 'radial' in data['composition_type']:
            generator_config = RadialImageConfig(**data.get('radial_image_config', {}))
        
        layout = data.get('layout', [1, 1])  # 默认1x1布局

        return cls(
            layout=layout,
            # panel_configs=panel_configs, # Removed old panel_configs
            element_configs=element_configs, # Added element_configs
            basic_attributes_distribution=basic_attrs,
            composition_type=data['composition_type'],
            parent=None,
            simple_image_config=generator_config if isinstance(generator_config, SimpleImageConfig) else None,
            chaining_image_config=generator_config if isinstance(generator_config, ChainingImageConfig) else None,
            enclosing_image_config=generator_config if isinstance(generator_config, EnclosingImageConfig) else None,
            parallel_image_config=generator_config if isinstance(generator_config, ParallelImageConfig) else None,
            radial_image_config=generator_config if isinstance(generator_config, RadialImageConfig) else None
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """递归地将PanelConfig及其嵌套对象转为字典"""
        # Manually serialize BasicAttributesDistribution if it doesn't have to_dict
        basic_attrs_dist_dict = None
        if self.basic_attributes_distribution:
            if hasattr(self.basic_attributes_distribution, 'to_dict'):
                basic_attrs_dist_dict = self.basic_attributes_distribution.to_dict()
            elif isinstance(self.basic_attributes_distribution, BasicAttributesDistribution):
                 basic_attrs_dist_dict = {
                    'color_distribution': self.basic_attributes_distribution.color_distribution,
                    'lightness_distribution': self.basic_attributes_distribution.lightness_distribution,
                    'background_lightness_distribution': self.basic_attributes_distribution.background_lightness_distribution,
                    'pattern_distribution': self.basic_attributes_distribution.pattern_distribution,
                    'outline_distribution': self.basic_attributes_distribution.outline_distribution,
                    'shape_distribution': self.basic_attributes_distribution.shape_distribution
                }
            else: # Keep original if it's already a dict or other serializable type
                basic_attrs_dist_dict = self.basic_attributes_distribution

        data = {
            'layout': self.layout,
            'basic_attributes_distribution': basic_attrs_dist_dict, # Use the serialized dict
            'composition_type': self.composition_type,
            # Serialize element_configs
            'element_configs': [elem.to_dict() if hasattr(elem, 'to_dict') else elem for elem in self.element_configs]
        }

        # 添加各种生成器配置，如果存在的话
        if self.simple_image_config:
            data['simple_image_config'] = self.simple_image_config.to_dict() if hasattr(self.simple_image_config, 'to_dict') else self.simple_image_config
        if self.chaining_image_config:
            # Ensure elements within chaining config are also serialized
            chaining_dict = self.chaining_image_config.to_dict() if hasattr(self.chaining_image_config, 'to_dict') else self.chaining_image_config
            if isinstance(chaining_dict, dict) and 'elements' in chaining_dict:
                chaining_dict['elements'] = [elem.to_dict() if hasattr(elem, 'to_dict') else elem for elem in chaining_dict['elements']]
            data['chaining_image_config'] = chaining_dict
        if self.enclosing_image_config:
            data['enclosing_image_config'] = self.enclosing_image_config.to_dict() if hasattr(self.enclosing_image_config, 'to_dict') else self.enclosing_image_config
        if self.parallel_image_config:
            data['parallel_image_config'] = self.parallel_image_config.to_dict() if hasattr(self.parallel_image_config, 'to_dict') else self.parallel_image_config
        if self.radial_image_config:
            data['radial_image_config'] = self.radial_image_config.to_dict() if hasattr(self.radial_image_config, 'to_dict') else self.radial_image_config

        return data