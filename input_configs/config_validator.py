from typing import Dict, List
from .base_config import BaseConfig, BasicAttributesDistribution

def validate_distribution(dist: List[float], name: str) -> bool:
    """验证分布列表的有效性"""
    if not dist or not isinstance(dist, list):
        raise ValueError(f'{name} 必须是非空列表')
    if not all(isinstance(x, (int, float)) for x in dist):
        raise ValueError(f'{name} 必须只包含数值')
    if abs(sum(dist) - 1.0) > 1e-6:
        raise ValueError(f'{name} 的概率和必须等于1')
    if any(x < 0 for x in dist):
        raise ValueError(f'{name} 不能包含负数')
    return True

def validate_basic_attributes(attrs: BasicAttributesDistribution) -> bool:
    """验证基本属性分布的有效性"""
    validate_distribution(attrs.color_distribution, '颜色分布')
    validate_distribution(attrs.lightness_distribution, '亮度分布')
    validate_distribution(attrs.background_lightness_distribution, '背景亮度分布')
    validate_distribution(attrs.pattern_distribution, '图案分布')
    validate_distribution(attrs.outline_distribution, '轮廓分布')
    validate_distribution(attrs.shape_distribution, '形状分布')
    return True

def validate_base_config(config: BaseConfig) -> bool:
    """验证基础配置的有效性"""
    if not config.layout or len(config.layout) != 2:
        raise ValueError('布局必须是包含两个元素的列表')
    if not all(isinstance(x, int) and x > 0 for x in config.layout):
        raise ValueError('布局必须是正整数')
    
    if not config.panel_configs:
        raise ValueError('面板配置列表不能为空')
    if len(config.panel_configs) != config.layout[0] * config.layout[1]:
        raise ValueError('面板配置数量必须与布局大小匹配')
    
    validate_basic_attributes(config.basic_attributes_distribution)
    return True