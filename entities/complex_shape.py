from typing import List, Optional

from matplotlib.pyplot import isinteractive
from numpy import shape
import shapely
from entities.entity import ClosedShape, VisibleShape
import img_params
from tikz_converters import ComplexShapeConverter
from shapely.affinity import scale


class ComplexShape(ClosedShape):
    dataset_annotation_categories = [
        "pattern",
        "color",
        "lightness",
        "pattern_color",
        "pattern_lightness",
        "outline",
        "outline_color",
        "outline_thickness",
        "outline_lightness",
    ]  # attributes that can be directly interpreted as categories in dataset annotations

    serialized_fields = [
        "uid",
        "position",
        "base_geometry",
    ] + dataset_annotation_categories

    def __init__(
        self,
        color: Optional[img_params.Color] = None,
        pattern: Optional[img_params.Pattern] = None,
        lightness: Optional[img_params.Lightness] = None,
        outline=None,
        outline_lightness=None,
        pattern_color=None,
        pattern_lightness=None,
        outline_color=None,
        outline_thickness=None,
        geometry:shapely.geometry.base.BaseGeometry = None
    ) -> None:
        super().__init__(
            tikz_converter=ComplexShapeConverter(),
            color = color,
            lightness=lightness,
            outline=outline,
            outline_color=outline_color,
            outline_lightness=outline_lightness,
            outline_thickness=outline_thickness,
            pattern=pattern,
            pattern_color=pattern_color,
            pattern_lightness=pattern_lightness,
        )
        if geometry is not None:
            self._base_geometry = geometry

    @staticmethod
    def from_overlapping_geometries(shape1: shapely.geometry.base.BaseGeometry, shape2: shapely.geometry.base.BaseGeometry)->List[shapely.geometry.base.BaseGeometry]:
        overlaping_base_geometry = shape1.intersection(shape2)
        if isinstance(overlaping_base_geometry,shapely.MultiPolygon):
            overlapping_geoms = list(overlaping_base_geometry.geoms)
        else:
            overlapping_geoms = [overlaping_base_geometry]
        overlaps = [ComplexShape(geometry=geom) for geom in overlapping_geoms]
        
        return overlaps

    @property
    def center(self):
        return self._base_geometry.centroid.coords[0]

    @property
    def position(self):
        return self.center

    def expand(self, ratio):
        self._base_geometry = scale(self._base_geometry, xfact=ratio, yfact=ratio, origin="center")
        return self

    def expand_fixed(self, length):
        self._base_geometry = self._base_geometry.buffer(length)
        return self
