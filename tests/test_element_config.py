import unittest
import json
from pathlib import Path
import tempfile
import sys

# This assumes 'input_configs' is a package located in the parent directory of 'tests'
# or accessible via PYTHONPATH.
# If your project structure is /d:/MyProjects/Research/input_configs and /d:/MyProjects/Research/tests
# you might need to adjust sys.path if running tests directly from the tests folder.
# A common practice is to run tests from the project root (e.g., /d:/MyProjects/Research/)
# using a command like 'python -m unittest discover tests'
# For simplicity, if 'input_configs' is not found, we add its parent to sys.path.
try:
    from input_configs.element_config import ElementConfig
    from input_configs.basic_attributes_distribution import BasicAttributesDistribution
except ImportError:
    # Assuming the script is in /d:/MyProjects/Research/tests
    # and input_configs is in /d:/MyProjects/Research/input_configs
    # Add /d:/MyProjects/Research/ to sys.path
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    from input_configs.element_config import ElementConfig
    from input_configs.basic_attributes_distribution import BasicAttributesDistribution


class TestElementConfig(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to store test JSON files
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.test_dir.name)

        # Sample BasicAttributesDistribution data
        self.basic_attrs_dict = {
            "color_distribution": [0.1, 0.9],
            "lightness_distribution": [0.5, 0.5],
            "background_lightness_distribution": [1.0],
            "pattern_distribution": [0.2, 0.8],
            "outline_distribution": [0.7, 0.3],
            "shape_distribution": [0.4, 0.6]
        }
        # self.basic_attrs_obj = BasicAttributesDistribution(**self.basic_attrs_dict) # Not needed directly for these tests

        # Sample ElementConfig data
        self.element_config_data_dict = {
            "basic_attributes_distribution": self.basic_attrs_dict,
            "composition_type": {"simple": 0.8, "complex": 0.2}
        }
        
        self.element_config_data_no_basic_attrs_dict = {
            "composition_type": {"simple": 1.0}
            # basic_attributes_distribution will be default (None)
        }


        # Create a sample element_config.json file
        self.sample_element_json_path = self.test_path / "sample_element.json"
        with open(self.sample_element_json_path, 'w') as f:
            json.dump(self.element_config_data_dict, f, indent=4)
            
        self.sample_element_no_basic_attrs_json_path = self.test_path / "sample_element_no_basic.json"
        with open(self.sample_element_no_basic_attrs_json_path, 'w') as f:
            json.dump(self.element_config_data_no_basic_attrs_dict, f, indent=4)


    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_from_json_with_basic_attrs(self):
        element_config = ElementConfig.from_json(str(self.sample_element_json_path))
        self.assertIsInstance(element_config, ElementConfig)
        self.assertIsInstance(element_config.basic_attributes_distribution, BasicAttributesDistribution)
        self.assertEqual(element_config.color_distribution, self.basic_attrs_dict["color_distribution"])
        self.assertEqual(element_config.composition_type, self.element_config_data_dict["composition_type"])

    def test_from_json_without_basic_attrs(self):
        element_config = ElementConfig.from_json(str(self.sample_element_no_basic_attrs_json_path))
        self.assertIsInstance(element_config, ElementConfig)
        self.assertIsNone(element_config.basic_attributes_distribution) # Default is None
        self.assertEqual(element_config.composition_type, self.element_config_data_no_basic_attrs_dict["composition_type"])


    def test_from_dict_with_basic_attrs(self):
        # from_dict should now correctly instantiate BasicAttributesDistribution
        element_config = ElementConfig.from_dict(self.element_config_data_dict)
        self.assertIsInstance(element_config, ElementConfig)
        self.assertIsInstance(element_config.basic_attributes_distribution, BasicAttributesDistribution)
        self.assertEqual(element_config.color_distribution, self.basic_attrs_dict["color_distribution"])
        self.assertEqual(element_config.composition_type, self.element_config_data_dict["composition_type"])
        
    def test_from_dict_without_basic_attrs(self):
        element_config_no_basic = ElementConfig.from_dict(self.element_config_data_no_basic_attrs_dict)
        self.assertIsInstance(element_config_no_basic, ElementConfig)
        self.assertIsNone(element_config_no_basic.basic_attributes_distribution) # Default is None
        self.assertEqual(element_config_no_basic.composition_type, self.element_config_data_no_basic_attrs_dict["composition_type"])

    def test_to_dict_with_basic_attrs(self):
        element_config = ElementConfig.from_json(str(self.sample_element_json_path))
        config_dict = element_config.to_dict()

        expected_dict = {
            "basic_attributes_distribution": self.basic_attrs_dict, # asdict converts BasicAttributesDistribution object to dict
            "composition_type": self.element_config_data_dict["composition_type"]
        }
        self.assertEqual(config_dict, expected_dict)

    def test_to_dict_without_basic_attrs(self):
        element_config_no_basic = ElementConfig.from_json(str(self.sample_element_no_basic_attrs_json_path))
        config_dict_no_basic = element_config_no_basic.to_dict()
        expected_dict_no_basic = {
            "basic_attributes_distribution": None, # asdict on None field returns None
            "composition_type": self.element_config_data_no_basic_attrs_dict["composition_type"]
        }
        self.assertEqual(config_dict_no_basic, expected_dict_no_basic)

    def test_to_json_with_basic_attrs(self):
        element_config = ElementConfig.from_json(str(self.sample_element_json_path))
        
        output_json_path = self.test_path / "output_element.json"
        element_config.to_json(str(output_json_path))

        self.assertTrue(output_json_path.exists())

        with open(output_json_path, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data, element_config.to_dict()) # Compare loaded JSON with to_dict output

    def test_to_json_without_basic_attrs(self):
        element_config = ElementConfig.from_json(str(self.sample_element_no_basic_attrs_json_path))
        
        output_json_path = self.test_path / "output_element_no_basic.json"
        element_config.to_json(str(output_json_path))

        self.assertTrue(output_json_path.exists())

        with open(output_json_path, 'r') as f:
            loaded_data = json.load(f)
            
        self.assertEqual(loaded_data, element_config.to_dict())


if __name__ == '__main__':
    # This allows running the tests directly from this file: python tests/test_element_config.py
    # For running all tests in the 'tests' directory, use: python -m unittest discover tests
    unittest.main() 