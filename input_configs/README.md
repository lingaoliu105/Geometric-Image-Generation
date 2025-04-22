# 配置系统说明

## 配置文件结构

配置系统主要包含以下组件：

- `BaseConfig`: 基础配置类，包含布局、面板配置和基本属性分布
- `BasicAttributesDistribution`: 基本属性分布类，定义各种视觉属性的概率分布
- `ConfigValidator`: 配置验证器，确保配置数据的正确性

## 使用方法

### 1. 创建配置文件

创建一个JSON格式的配置文件，包含以下字段：

```json
{
    "layout": [行数, 列数],
    "panel_configs": [面板配置文件路径列表],
    "basic_attributes_distribution": {
        "color_distribution": [...],
        "lightness_distribution": [...],
        "background_lightness_distribution": [...],
        "pattern_distribution": [...],
        "outline_distribution": [...],
        "shape_distribution": [...]
    }
}
```

### 2. 加载配置

```python
from input_configs import BaseConfig

# 从JSON文件加载配置
config = BaseConfig.from_json('path/to/config.json')
```

### 3. 验证配置

```python
from input_configs.config_validator import validate_base_config

# 验证配置的有效性
validate_base_config(config)
```

## 注意事项

1. 所有分布列表的概率和必须等于1
2. 面板配置数量必须与布局大小匹配
3. 所有概率值必须为非负数
4. 布局必须是两个正整数的列表

## 示例

参考 `example_configs` 目录下的示例配置文件。