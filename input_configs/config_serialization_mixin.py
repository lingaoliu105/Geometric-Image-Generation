from dataclasses import asdict, fields, is_dataclass, MISSING, Field
from typing import Any, Dict, TypeVar, Type, Callable, Optional, List
import json
from pathlib import Path

# 导入 BaseGeneratorConfig 用于类型提示和处理，需要确保它能被正确解析
# from .generator_configs import BaseGeneratorConfig 
# 暂时注释掉，因为我们还未处理循环导入或更优雅的导入结构
# 后续在整合时需要确保 generator_configs 和其他配置类能正确交互

T = TypeVar('T')

class ConfigSerializationMixin:
    """
    A Mixin class to provide common JSON and dictionary serialization/deserialization logic
    for dataclass-based configuration objects.
    """

    # --- Public API ---

    @classmethod
    def from_json(cls: Type[T], json_path: str) -> T:
        """Create an instance from a JSON file."""
        path = Path(json_path)
        if not path.is_file():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data, curr_path=path.parent)

    def save_to_json(self, json_path: str, indent: int = 4) -> None:
        """Serialize the instance to a JSON file."""
        output_path = Path(json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=indent)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any], curr_path: Optional[Path] = None) -> T:
        """
        Create an instance from a dictionary.
        This method relies on _preprocess_data_for_from_dict to prepare the data
        and then initializes the dataclass.
        Subclasses should primarily override _preprocess_data_for_from_dict and 
        _get_generator_config_field_names for custom deserialization logic.
        """
        init_args = {}
        # Process data using the hook, which subclasses can override for complex types
        processed_data = cls._preprocess_data_for_from_dict(data, curr_path=curr_path)

        cls_fields: Dict[str, Field] = {f.name: f for f in fields(cls)}

        for field_name, field_obj in cls_fields.items():
            if not field_obj.init:  # Skip fields that are not part of the constructor (init=False)
                continue
            
            if field_name in processed_data:
                init_args[field_name] = processed_data[field_name]
            elif field_obj.default is not MISSING:
                init_args[field_name] = field_obj.default
            elif field_obj.default_factory is not MISSING:
                init_args[field_name] = field_obj.default_factory()
            # If an init=True field is not in processed_data and has no default,
            # the cls(**init_args) call will correctly raise a TypeError for missing arguments.

        try:
            instance = cls(**init_args)
        except TypeError as e:
            # Provide more context if instantiation fails
            current_fields = {f.name for f in fields(cls)}
            missing_fields = [f.name for f in fields(cls) 
                              if f.init and f.name not in init_args and 
                                 f.default is MISSING and 
                                 f.default_factory is MISSING]
            extra_fields = [k for k in init_args if k not in current_fields]
            
            error_msg = f"Error instantiating {cls.__name__}: {e}.\n"
            if missing_fields:
                error_msg += f"Missing required fields not provided in data and without defaults: {missing_fields}.\n"
            if extra_fields:
                error_msg += f"Provided extra fields not defined in dataclass: {extra_fields}.\n"
            error_msg += f"Attempted to initialize with processed args: {list(init_args.keys())}"
            raise TypeError(error_msg) from e
            
        # After successful instantiation, set parent references if the method exists
        if hasattr(instance, "_set_child_parent_references") and callable(getattr(instance, "_set_child_parent_references")):
            instance._set_child_parent_references()
            
        return instance

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the instance to a dictionary.
        This method uses asdict and then applies postprocessing via _postprocess_data_for_to_dict.
        Subclasses should primarily override _postprocess_data_for_to_dict and 
        _get_generator_config_field_names for custom serialization logic.
        """
        # Use dataclasses.asdict for initial conversion.
        # It handles basic dataclass to dict conversion well.
        # _postprocess_data_for_to_dict will then handle nested custom objects.
        initial_dict = asdict(self)
        return self._postprocess_data_for_to_dict(initial_dict)

    # --- Internal methods for subclasses to override/use ---

    @classmethod
    def _get_generator_config_field_names(cls) -> List[str]:
        """
        Returns a list of field names that correspond to generator configurations.
        Subclasses should override this if they have such fields.
        Example: return ["simple_image_config", "chaining_image_config"]
        """
        return []

    @classmethod
    def _preprocess_data_for_from_dict(cls: Type[T], data: Dict[str, Any], curr_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Hook for subclasses to preprocess data before it's used to initialize fields in from_dict.
        This is where nested configs (like generator_configs or other custom types) should be instantiated from their dict form.
        The base implementation handles generator_configs if _get_generator_config_field_names is implemented.
        """
        processed_data = data.copy() # Work on a copy

        try:
            # Attempt to import BaseGeneratorConfig dynamically to handle its instantiation.
            # This helps avoid direct circular dependencies at the module level.
            from .generator_configs import BaseGeneratorConfig
            generator_config_cls = BaseGeneratorConfig
        except ImportError:
            generator_config_cls = None 
            # print(f"Warning: BaseGeneratorConfig could not be imported. Generator config fields will be passed as dicts if not handled by subclass overrides.")

        generator_field_names = cls._get_generator_config_field_names()
        if generator_config_cls and generator_field_names:
            for field_name in generator_field_names:
                if field_name in processed_data and isinstance(processed_data[field_name], dict):
                    processed_data[field_name] = generator_config_cls.from_dict(
                        processed_data[field_name],
                        generator_config_type_name=field_name, 
                        curr_path=curr_path
                    )
        
        # Subclasses can extend this method to handle other specific field types.
        # For example, to instantiate BasicAttributesDistribution if it was complex:
        # if 'basic_attributes_distribution' in processed_data and \
        #    isinstance(processed_data['basic_attributes_distribution'], dict):
        #     from .basic_attributes_distribution import BasicAttributesDistribution
        #     processed_data['basic_attributes_distribution'] = BasicAttributesDistribution(**processed_data['basic_attributes_distribution'])

        return processed_data

    def _postprocess_data_for_to_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook for subclasses to postprocess the dictionary (e.g., created by asdict)
        before it's returned by to_dict.
        This is where nested config objects should call their own to_dict methods if asdict doesn't suffice.
        The base implementation handles generator_configs if _get_generator_config_field_names is implemented
        and the generator objects have a to_dict method.
        """
        processed_data = data.copy() # Work on a copy

        generator_field_names = self._get_generator_config_field_names()
        if generator_field_names:
            for field_name in generator_field_names:
                # The `data` here comes from asdict, so `processed_data[field_name]` is the attribute value itself.
                field_value = getattr(self, field_name, None) 
                if field_value is not None and hasattr(field_value, 'to_dict') and callable(getattr(field_value, 'to_dict')):
                    processed_data[field_name] = field_value.to_dict()
                # If it's None or doesn't have to_dict, asdict would have set it to None or its simple representation.

        # Subclasses can extend this method to handle other specific field types.
        # For example, if BasicAttributesDistribution needed special serialization:
        # if 'basic_attributes_distribution' in processed_data and hasattr(self.basic_attributes_distribution, 'to_dict'):
        #    processed_data['basic_attributes_distribution'] = self.basic_attributes_distribution.to_dict()
        # elif 'basic_attributes_distribution' in processed_data and is_dataclass(self.basic_attributes_distribution):
        #    # asdict should handle simple dataclasses correctly, but explicit handling can be added.
        #    processed_data['basic_attributes_distribution'] = asdict(self.basic_attributes_distribution)

        return processed_data


