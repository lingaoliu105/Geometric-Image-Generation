# 迁移到合并的 image_generators 模块

## 概述

为了解决循环依赖问题，所有 `image_generators` 包中的文件已经合并到单个文件 `image_generators_merged.py` 中。

## 文件结构

合并后的文件包含：
- 基类 `ImageGenerator`
- 所有生成器子类：
  - `SimpleImageGenerator`
  - `ChainingImageGenerator`
  - `EnclosingImageGenerator`
  - `RandomImageGenerator`
  - `RadialImageGenerator`
  - `ParallelImageGenerator`
  - `BorderImageGenerator`
- 辅助函数：
  - `get_image_generator()`
  - `generate_shape_group()`

## 如何迁移

### 1. 更新导入语句

**之前：**
```python
from image_generators import ChainingImageGenerator
from image_generators import generate_shape_group
from image_generators.chaining_image_generator import ChainingImageGenerator
```

**之后：**
```python
from image_generators_merged import ChainingImageGenerator
from image_generators_merged import generate_shape_group
# 或者
from image_generators_merged import *
```

### 2. 替换特定文件的导入

如果你的代码中有类似这样的导入：
```python
from image_generators import generate_shape_group
from image_generators import get_image_generator
```

改为：
```python
from image_generators_merged import generate_shape_group
from image_generators_merged import get_image_generator
```

### 3. 处理 chaining_image_generator.py 中的修改

在原始的 `chaining_image_generator.py` 中，你已经做了以下修改：
```python
generation_config.step_into_config_scope("chaining_image_config")
from image_generators import generate_shape_group
element_grp = generate_shape_group(GenerationConfig.current_config)
```

在合并的文件中，这已经被更新为：
```python
generation_config.step_into_config_scope("chaining_image_config")
element_grp = generate_shape_group()
```

### 4. 删除旧的 image_generators 目录（可选）

一旦确认新的合并文件工作正常，你可以：
1. 备份原始的 `image_generators` 目录
2. 删除或重命名原始目录，避免混淆

### 5. 更新其他文件中的引用

搜索项目中所有使用 `image_generators` 的地方：
```bash
# 查找所有引用 image_generators 的文件
grep -r "from image_generators" .
grep -r "import image_generators" .
```

## 优势

1. **解决循环依赖**：所有类和函数现在都在同一个文件中，避免了模块间的循环引用
2. **更简单的导入**：只需要从一个文件导入所需的类
3. **更容易维护**：所有相关代码在一个地方

## 注意事项

1. 确保更新所有引用 `image_generators` 包的地方
2. 运行测试确保功能正常
3. 合并后的文件较大（约 850 行），但解决了循环依赖问题

## 示例用法

```python
# 导入所需的类和函数
from image_generators_merged import (
    SimpleImageGenerator,
    ChainingImageGenerator,
    generate_shape_group,
    get_image_generator
)

# 使用方式保持不变
generator = ChainingImageGenerator()
shape_group = generator.generate()

# 或者
shape_group = generate_shape_group()
``` 