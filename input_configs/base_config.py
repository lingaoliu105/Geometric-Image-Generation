from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import os

@dataclass
class BasicAttributesDistribution:
    color_distribution: List[float] = field(default_factory=lambda: [0.0])
    lightness_distribution: List[float] = field(default_factory=lambda: [0.0])
    background_lightness_distribution: List[float] = field(default_factory=lambda: [0.0])
    pattern_distribution: List[float] = field(default_factory=lambda: [0.0])
    outline_distribution: List[float] = field(default_factory=lambda: [0.0])
    shape_distribution: List[float] = field(default_factory=lambda: [0.0])

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
        
        # 处理panel_configs中的文件路径引用
        panel_configs = []
        json_dir = Path(json_path).parent
        
        for pc in data['panel_configs']:
            if isinstance(pc, str) and pc.endswith('.json'):
                # 处理文件路径引用
                file_path = json_dir / pc
                if file_path.exists():
                    # 导入PanelConfig类
                    from .panel_config import PanelConfig
                    # 加载panel配置文件
                    panel_config = PanelConfig.from_json(str(file_path))
                    panel_configs.append(panel_config)
                else:
                    print(f"Warning: Referenced panel config file not found: {file_path}")
                    panel_configs.append(pc)
            else:
                panel_configs.append(pc)
        
        return cls(
            layout=data['layout'],
            panel_configs=panel_configs,
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

    def save_to_json(self, json_path: str) -> None:
        """Save the current BaseConfig instance to a JSON file."""
        # Ensure the output directory exists
        output_path = Path(json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert the object to a dictionary
        config_dict = self.to_dict()
        
        # Write the dictionary to the JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def read_input_folder(cls, input_folder: str) -> Dict[str, Any]:
        """Read all JSON files from input folder and merge them into a single dictionary
        
        如果JSON文件中包含文件路径引用，将读取引用文件并创建相应的配置对象
        """
        merged_data = {}
        input_path = Path(input_folder)
        
        if not input_path.exists() or not input_path.is_dir():
            raise ValueError(f"Input folder {input_folder} does not exist or is not a directory")
        
        # 处理所有JSON文件
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = Path(root) / file
                    merged_data.update(cls._process_json_file(file_path, input_path))
        
        return merged_data
    
    @classmethod
    def _process_json_file(cls, file_path: Path, base_path: Path) -> Dict[str, Any]:
        """处理单个JSON文件，解析其内容并处理文件引用"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            if not isinstance(data, dict):
                print(f"Warning: JSON file {file_path} does not contain a dictionary")
                return {}
                
            # 递归处理字典中的所有值，查找文件引用
            processed_data = cls._process_config_values(data, file_path.parent, base_path)
            return processed_data
            
        except json.JSONDecodeError:
            print(f"Warning: Could not parse JSON file {file_path}")
            return {}
    
    @classmethod
    def _process_config_values(cls, data: Dict[str, Any], current_dir: Path, base_path: Path) -> Dict[str, Any]:
        """递归处理配置字典中的值，解析文件引用并创建相应的配置对象"""
        result = {}
        
        for key, value in data.items():
            # 处理字符串值，检查是否为文件引用
            if isinstance(value, str) and value.endswith('.json'):
                # 尝试解析为文件路径
                try:
                    # 首先尝试相对于当前目录的路径
                    file_path = current_dir / value
                    if not file_path.exists():
                        # 然后尝试相对于基础目录的路径
                        file_path = base_path / value
                    
                    if file_path.exists():
                        # 读取引用的文件
                        with open(file_path, 'r') as f:
                            file_data = json.load(f)
                            
                        # 根据文件内容创建相应的配置对象
                        if 'element_type' in file_data:
                            # 创建ElementConfig
                            from .element_config import ElementConfig
                            result[key] = ElementConfig.from_dict(file_data)
                        elif 'composition_type' in file_data:
                            # 创建PanelConfig
                            from .panel_config import PanelConfig
                            result[key] = PanelConfig.from_dict(file_data)
                        else:
                            # 普通数据，直接使用
                            result[key] = file_data
                    else:
                        # 如果文件不存在，保留原始值
                        result[key] = value
                except Exception as e:
                    print(f"Warning: Error processing file reference {value}: {e}")
                    result[key] = value
            # 处理字典值，递归处理
            elif isinstance(value, dict):
                result[key] = cls._process_config_values(value, current_dir, base_path)
            # 处理列表值，递归处理列表中的每个元素
            elif isinstance(value, list):
                processed_list = []
                for item in value:
                    if isinstance(item, dict):
                        processed_list.append(cls._process_config_values(item, current_dir, base_path))
                    elif isinstance(item, str) and item.endswith('.json'):
                        # 处理列表中的文件引用
                        try:
                            file_path = current_dir / item
                            if not file_path.exists():
                                file_path = base_path / item
                                
                            if file_path.exists():
                                with open(file_path, 'r') as f:
                                    file_data = json.load(f)
                                    
                                if 'element_type' in file_data:
                                    from .element_config import ElementConfig
                                    processed_list.append(ElementConfig.from_dict(file_data))
                                elif 'composition_type' in file_data:
                                    from .panel_config import PanelConfig
                                    processed_list.append(PanelConfig.from_dict(file_data))
                                else:
                                    processed_list.append(file_data)
                            else:
                                processed_list.append(item)
                        except Exception as e:
                            print(f"Warning: Error processing file reference in list {item}: {e}")
                            processed_list.append(item)
                    else:
                        processed_list.append(item)
                result[key] = processed_list
            # 其他类型的值，直接使用
            else:
                result[key] = value
                
        return result
    
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
    def from_dict(cls, data: Dict[str, Any], base_dir: str = None) -> 'BaseConfig':
        """递归地从字典数据创建BaseConfig及其嵌套对象
        
        Args:
            data: 配置数据字典
            base_dir: 基础目录路径，用于解析相对路径引用的文件
            
        Returns:
            BaseConfig实例
        """
        # 处理基本属性分布
        basic_attrs_data = data.get('basic_attributes_distribution', {})
        if isinstance(basic_attrs_data, str) and basic_attrs_data.endswith('.json'):
            # 如果basic_attributes_distribution是文件路径，读取该文件
            if base_dir:
                file_path = Path(base_dir) / basic_attrs_data
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        basic_attrs_data = json.load(f)
        
        basic_attrs = BasicAttributesDistribution(**basic_attrs_data)
        
        # 处理面板配置
        panel_configs = []
        for pc in data.get('panel_configs', []):
            if isinstance(pc, dict):
                # 延迟导入PanelConfig，避免循环导入
                from .panel_config import PanelConfig
                panel_configs.append(PanelConfig.from_dict(pc, base_dir))
            elif isinstance(pc, str) and pc.endswith('.json'):
                # 处理文件路径引用
                if base_dir:
                    file_path = Path(base_dir) / pc
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            panel_data = json.load(f)
                        # 使用文件所在目录作为新的基础目录
                        new_base_dir = str(file_path.parent)
                        from .panel_config import PanelConfig
                        panel_configs.append(PanelConfig.from_dict(panel_data, new_base_dir))
                    else:
                        print(f"Warning: Referenced file not found: {file_path}")
            else:
                panel_configs.append(pc)
                
        return cls(
            layout=data['layout'],
            panel_configs=panel_configs,
            basic_attributes_distribution=basic_attrs
        )

    def to_dict(self) -> Dict[str, Any]:
        """递归地将BaseConfig及其嵌套对象转为字典"""
        panel_configs_list = []
        for pc in self.panel_configs:
            if hasattr(pc, 'to_dict'):
                panel_configs_list.append(pc.to_dict())
            else:
                panel_configs_list.append(pc)
                
        return {
            'layout': self.layout,
            'panel_configs': panel_configs_list,
            'basic_attributes_distribution': {
                'color_distribution': self.basic_attributes_distribution.color_distribution,
                'lightness_distribution': self.basic_attributes_distribution.lightness_distribution,
                'background_lightness_distribution': self.basic_attributes_distribution.background_lightness_distribution,
                'pattern_distribution': self.basic_attributes_distribution.pattern_distribution,
                'outline_distribution': self.basic_attributes_distribution.outline_distribution,
                'shape_distribution': self.basic_attributes_distribution.shape_distribution
            }
        }