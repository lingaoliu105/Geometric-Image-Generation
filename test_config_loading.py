import os
import json
from pathlib import Path
from input_configs.base_config import BaseConfig

def main():
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    
    # 加载基础配置文件
    base_json_path = current_dir / 'input' / 'base.json'
    print(f"加载配置文件: {base_json_path}")
    
    # 使用修改后的from_json方法加载配置
    config = BaseConfig.from_json(str(base_json_path))
    # Assign the source path to the config object for hierarchy generation
    config._source_path = str(base_json_path)
    
    # 打印配置信息，验证文件路径已被替换为实际内容
    print("\n配置加载完成，检查panel_configs:")
    for i, panel in enumerate(config.panel_configs):#
        print(f"\nPanel {i+1}:")
        print(f"  类型: {type(panel).__name__}")
        print(f"  组合类型: {panel.composition_type}")
        
        # 检查chaining_image_config
        if panel.chaining_image_config:
            print(f"  Chaining配置:")
            print(f"    元素数量: {panel.chaining_image_config.element_num}")
            print(f"    链形状: {panel.chaining_image_config.chain_shape}")
            
            
            # 检查elements是否已被加载为对象而非文件路径
            if hasattr(panel.chaining_image_config, 'sub_elements'):
                print(f"    元素列表 (sub_elements):")
                for j, elem in enumerate(panel.chaining_image_config.sub_elements):
                    # 打印元素类型和内容
                    elem_type = type(elem).__name__
                    print(f"      元素 {j+1}: {elem_type}")

                    # 检查并打印父对象信息
                    parent_info_str = "        父对象: "
                    if hasattr(elem, 'parent') and elem.parent is not None:
                        parent_info_str += f"{type(elem.parent).__name__}"
                        if elem.parent == panel: # 'panel' is the PanelConfig from the outer loop
                            parent_info_str += f" (Panel ID: {panel.panel_id} - Correct)"
                        elif isinstance(elem.parent, ElementConfig): # Check if parent is an ElementConfig (for nested scenarios)
                            parent_info_str += " (Parent is an ElementConfig)"
                        else:
                            parent_info_str += " (Unexpected parent type or ID mismatch)"
                    else:
                        parent_info_str += "None or not set"
                    print(parent_info_str)
                    
                    # 如果是字符串，检查是否是文件路径
                    if isinstance(elem, str) and elem.endswith('.json'):
                        print(f"        文件路径: {elem}")
                    # 如果是对象，打印其属性
                    elif hasattr(elem, '__dict__'):
                        print(f"        属性: {list(elem.__dict__.keys())}")
    
    print("\n配置加载测试完成!")

    # 将加载的配置对象序列化为JSON文件
    output_file = current_dir / 'output_loaded_config.json' # Changed output filename for clarity
    print(f"\n将加载的配置序列化到: {output_file}")

    # 调用save_to_json方法直接保存配置对象
    config.save_to_json(str(output_file))
    print(f"配置序列化完成！输出文件: {output_file}")

    # 生成并保存配置层级结构
    hierarchy_output_file = current_dir / 'input' / 'hierachy.json'
    print(f"\n将配置层级结构保存到: {hierarchy_output_file}")
    config.save_hierarchy_to_json(str(hierarchy_output_file))

if __name__ == "__main__":
    main()