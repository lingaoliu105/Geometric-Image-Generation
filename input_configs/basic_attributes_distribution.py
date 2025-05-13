from dataclasses import dataclass, field, fields
from typing import List, Dict, Any


@dataclass
class BasicAttributesDistribution:
    color_distribution: List[float] = field(default_factory=lambda: [0.0])
    lightness_distribution: List[float] = field(default_factory=lambda: [0.0])
    background_lightness_distribution: List[float] = field(
        default_factory=lambda: [0.0]
    )
    pattern_distribution: List[float] = field(default_factory=lambda: [0.0])
    outline_distribution: List[float] = field(default_factory=lambda: [0.0])
    shape_distribution: List[float] = field(default_factory=lambda: [0.0])

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        for f_info in fields(self):
            data[f_info.name] = getattr(self, f_info.name)
        return data
