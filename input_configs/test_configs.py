import unittest
import json
from pathlib import Path
from .base_config import BaseConfig, BasicAttributesDistribution
from .config_validator import validate_base_config, validate_basic_attributes

class TestConfigSystem(unittest.TestCase):
    def setUp(self):
        self.example_config_path = Path(__file__).parent / 'example_configs' / 'base_config_example.json'
        
    def test_load_config(self):
        config = BaseConfig.from_json(str(self.example_config_path))
        self.assertEqual(config.layout, [2, 2])
        self.assertEqual(len(config.panel_configs), 4)
        
    def test_basic_attributes(self):
        config = BaseConfig.from_json(str(self.example_config_path))
        attrs = config.basic_attributes_distribution
        self.assertTrue(abs(sum(attrs.color_distribution) - 1.0) < 1e-6)
        self.assertTrue(abs(sum(attrs.lightness_distribution) - 1.0) < 1e-6)
        self.assertTrue(abs(sum(attrs.background_lightness_distribution) - 1.0) < 1e-6)
        self.assertTrue(abs(sum(attrs.pattern_distribution) - 1.0) < 1e-6)
        self.assertTrue(abs(sum(attrs.outline_distribution) - 1.0) < 1e-6)
        self.assertTrue(abs(sum(attrs.shape_distribution) - 1.0) < 1e-6)
        
    def test_config_validation(self):
        config = BaseConfig.from_json(str(self.example_config_path))
        self.assertTrue(validate_base_config(config))
        
    def test_save_config(self):
        config = BaseConfig.from_json(str(self.example_config_path))
        temp_path = Path(__file__).parent / 'temp_config.json'
        config.to_json(str(temp_path))
        
        # 验证保存的文件可以被正确加载
        loaded_config = BaseConfig.from_json(str(temp_path))
        self.assertEqual(config.layout, loaded_config.layout)
        
        # 清理临时文件
        temp_path.unlink()

if __name__ == '__main__':
    unittest.main()