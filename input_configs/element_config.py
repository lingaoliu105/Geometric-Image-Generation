from dataclasses import dataclass, field, fields, asdict, is_dataclass
from typing import Dict, Optional, Any, List
from pathlib import Path

from input_configs.basic_attributes_distribution import BasicAttributesDistribution
from input_configs.config_serialization_mixin import ConfigSerializationMixin
from input_configs.generator_configs import BaseGeneratorConfig, ChainingImageConfig, EnclosingImageConfig, ParallelImageConfig, RadialImageConfig, SimpleImageConfig

@dataclass
class ElementConfig(ConfigSerializationMixin):
    """Configuration for an element in the panel"""
    basic_attributes_distribution: Optional[BasicAttributesDistribution] = None
    composition_type: Dict[str,float] = field(default_factory=lambda:{"simple":1.0})

    simple_image_config: Optional["SimpleImageConfig"] = None
    chaining_image_config: Optional["ChainingImageConfig"] = None
    enclosing_image_config: Optional["EnclosingImageConfig"] = None
    parallel_image_config: Optional["ParallelImageConfig"] = None
    radial_image_config: Optional["RadialImageConfig"] = None

    # Parent attribute, not initialized from JSON, not serialized, set programmatically
    parent: Optional[Any] = field(default=None, init=False, repr=False, compare=False)

    @classmethod
    def _get_generator_config_field_names(cls) -> List[str]:
        return [
            "simple_image_config",
            "chaining_image_config",
            "enclosing_image_config",
            "parallel_image_config",
            "radial_image_config",
        ]

    @classmethod
    def _preprocess_data_for_from_dict(cls, data: Dict[str, Any], curr_path: Optional[Path] = None) -> Dict[str, Any]:
        processed_data = super()._preprocess_data_for_from_dict(data, curr_path)

        # Handle BasicAttributesDistribution instantiation
        if 'basic_attributes_distribution' in processed_data and \
           isinstance(processed_data['basic_attributes_distribution'], dict):
            processed_data['basic_attributes_distribution'] = BasicAttributesDistribution(**processed_data['basic_attributes_distribution'])
        elif 'basic_attributes_distribution' not in processed_data:
             processed_data['basic_attributes_distribution'] = None

        return processed_data

    def to_dict(self) -> Dict[str, Any]:
        """Custom to_dict to handle parent and nested generator configs correctly."""
        data = {}
        generator_field_names = self._get_generator_config_field_names()

        for f_info in fields(self):
            field_name = f_info.name
            if field_name == 'parent': # Explicitly skip the parent field
                continue
            
            field_value = getattr(self, field_name)

            if field_value is None:
                data[field_name] = None
            elif field_name in generator_field_names:
                # These are instances of classes inheriting from BaseGeneratorConfig (like SimpleImageConfig)
                # We need to call their to_dict method (which BaseGeneratorConfig should have).
                if hasattr(field_value, 'to_dict') and callable(getattr(field_value, 'to_dict')):
                    data[field_name] = field_value.to_dict()
                else: # Fallback if to_dict is missing, though unlikely for these types
                    data[field_name] = asdict(field_value) if is_dataclass(field_value) else field_value
            elif isinstance(field_value, BasicAttributesDistribution):
                data[field_name] = field_value.to_dict()
            elif is_dataclass(field_value):
                 # For other potential nested dataclasses not covered above (though unlikely in current structure)
                data[field_name] = asdict(field_value)
            else:
                # This covers simple types like dict, list, str, int, float, bool
                data[field_name] = field_value
        
        # We are not calling super()._postprocess_data_for_to_dict() here because we have fully defined
        # the serialization for ElementConfig. If Mixin's postprocess had other generic logic, we might reconsider.
        return data

    def _set_child_parent_references(self) -> None:
        """Sets the parent reference for child ElementConfigs and recursively calls this method on them."""
        # ElementConfig itself can own GeneratorConfigs, which in turn own sub_elements (other ElementConfigs)
        for gen_cfg_field_name in self._get_generator_config_field_names():
            generator_config = getattr(self, gen_cfg_field_name, None)
            if generator_config and hasattr(generator_config, 'sub_elements'):
                for sub_element_cfg in generator_config.sub_elements:
                    if isinstance(sub_element_cfg, ElementConfig):
                        sub_element_cfg.parent = self # `self` is the current ElementConfig instance
                        # Recursively set parent references for children of this sub_element
                        sub_element_cfg._set_child_parent_references()

    # from_json, to_json, from_dict, to_dict are now inherited from ConfigSerializationMixin
    # Original from_json relied on cls.from_dict(data, curr_path=Path(json_path))
    # Original from_dict logic:
    #     processed_data = data.copy()
    #     if 'basic_attributes_distribution' in processed_data and \
    #        isinstance(processed_data['basic_attributes_distribution'], dict):
    #         processed_data['basic_attributes_distribution'] = BasicAttributesDistribution(**processed_data['basic_attributes_distribution'])
    #     generator_config_fields = [...] # Handled by Mixin now
    #     init_args = {}
    #     for f in fields(cls):
    #         if f.name in processed_data:
    #             if f.name in generator_config_fields: # Handled by Mixin now
    #                 init_args[f.name] = BaseGeneratorConfig.from_dict(processed_data[f.name],generator_config_type_name=f.name,curr_path=curr_path.parent)
    #             else: # ensure this logic is captured if not directly assigning
    #                 init_args[f.name] = processed_data[f.name]
    #     instance = cls(**init_args)
    #     return instance
    # Original to_dict used asdict(self), which is the base for Mixin's to_dict, then _postprocess_data_for_to_dict is called.
    # Since BasicAttributesDistribution is a dataclass, asdict should handle it correctly.
    # Generator configs are handled by the Mixin's _postprocess_data_for_to_dict via _get_generator_config_field_names.
    # So, _postprocess_data_for_to_dict might not need an override unless other custom serialization is needed.
