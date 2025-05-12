from dataclasses import dataclass, field
from typing import List


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
