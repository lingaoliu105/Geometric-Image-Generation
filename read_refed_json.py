import os
import json
import jsonref
from pathlib import Path

from input_configs.input_configs import BaseConfig

# 主文件路径
base_path = Path("input/base.json").resolve()

# 加载主文件并解析引用
with open(base_path, "r", encoding="utf-8") as f:
    data = json.load(f)

resolved = jsonref.JsonRef.replace_refs(data,base_uri=base_path.as_uri())

resolved_json_str = json.dumps(resolved,indent=4)
config = BaseConfig.model_validate_json(resolved_json_str)

print(config)
