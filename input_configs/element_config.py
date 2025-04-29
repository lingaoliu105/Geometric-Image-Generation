from dataclasses import dataclass, field
from typing import Dict, Optional, Union, Any, List
import json
from pathlib import Path
from .base_config import BaseConfig

@dataclass
class ElementConfig(BaseConfig):
    """Configuration for an element in the panel"""
    attributes: Dict[str, Any] = None
    parent: Optional[BaseConfig] = None
    children: List['ElementConfig'] = field(default_factory=list)
    
    @classmethod
    def from_json(cls, json_path: str) -> 'ElementConfig':
        """Create an ElementConfig instance from a JSON file"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            attributes=data['attributes']
        )
    
    @classmethod
    def from_dict(cls, data: dict, base_dir: str = None) -> 'ElementConfig':
        """从字典创建ElementConfig实例，支持处理文件引用
        
        Args:
            data: 配置数据字典
            base_dir: 基础目录路径，用于解析相对路径引用的文件
            
        Returns:
            ElementConfig实例
        """
        # 处理属性中的文件引用
        attributes = data.get('attributes', {})
        processed_attrs = {}
        
        for key, value in attributes.items():
            if isinstance(value, str) and value.endswith('.json') and base_dir:
                # 如果属性值是文件路径，尝试读取文件内容
                try:
                    file_path = Path(base_dir) / value
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            file_data = json.load(f)
                        processed_attrs[key] = file_data
                    else:
                        processed_attrs[key] = value
                except Exception as e:
                    print(f"Warning: Error processing file reference in ElementConfig: {e}")
                    processed_attrs[key] = value
            else:
                processed_attrs[key] = value
                
        # 处理children中的文件引用
        children = []
        for child in data.get('children', []):
            if isinstance(child, dict):
                children.append(cls.from_dict(child, base_dir))
            elif isinstance(child, str) and child.endswith('.json') and base_dir:
                # 如果child是文件路径，读取文件内容
                try:
                    file_path = Path(base_dir) / child
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            child_data = json.load(f)
                        # 使用文件所在目录作为新的基础目录
                        new_base_dir = str(file_path.parent)
                        children.append(cls.from_dict(child_data, new_base_dir))
                except Exception as e:
                    print(f"Warning: Error processing child file reference in ElementConfig: {e}")
            else:
                children.append(child)
                
        return cls(
            attributes=processed_attrs,
            children=children
        )

    def to_dict(self) -> dict:
        return {
            'attributes': self.attributes
        }
    
    def to_json(self, json_path: str) -> None:
        """Save the ElementConfig instance to a JSON file"""
        data = {
            'attributes': self.attributes
        }
        
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)