from input_configs.base_config import BaseConfig
import os

if __name__ == "__main__":
    input_folder = os.path.join(os.path.dirname(__file__), "input")
    output_json = os.path.join(os.path.dirname(__file__), "output_merged_config.json")

    # 1. 读取input文件夹所有json并合并
    merged_data = BaseConfig.read_input_folder(input_folder)
    print("合并后的原始数据:", merged_data)

    # 2. 递归实例化为配置对象树
    config_obj = BaseConfig.from_dict(merged_data)
    print("递归实例化后的对象:", config_obj)

    # 3. 递归转为dict并输出为json
    merged_dict = config_obj.to_dict()
    with open(output_json, "w", encoding="utf-8") as f:
        import json
        json.dump(merged_dict, f, indent=4, ensure_ascii=False)
    print(f"已输出合并后的配置到: {output_json}")