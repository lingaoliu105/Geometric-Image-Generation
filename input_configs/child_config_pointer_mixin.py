from typing import List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from input_configs.base_config import BaseConfig
    from input_configs.panel_config import PanelConfig
    from input_configs.element_config import ElementConfig

class ChildConfigPointerMixin:
    def __post_init__(self, *args, **kwargs):
        self.child_configs: List[Union["BaseConfig", "PanelConfig", "ElementConfig"]] = self.panel_config.child_configs if hasattr(self, 'panel_config') else []
        self.next_child_to_access: Optional[Union["BaseConfig", "PanelConfig", "ElementConfig"]] = self.child_configs[0] if self.child_configs else None
        self.next_child_to_access_index: int = 0
        
    def iterate_next_child_to_access(self):
        self.next_child_to_access = self.child_configs[self.next_child_to_access_index]
        self.next_child_to_access_index += 1