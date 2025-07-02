import binascii
from typing import List, Any, Dict
from pydantic import (
    BaseModel,
    RootModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
    NonNegativeInt,
)
from shapely import wkb
from shapely.geometry.base import BaseGeometry
from .base_geo_model import BaseGeoModel
from .line_junction_model import LineJunctionModel
from .intersect_point_model import IntersectPointModel


class GeoTransformModel(BaseGeoModel):

    line_tag: NonNegativeInt
    line_geom: str
    line_srid: NonNegativeInt
    start_point_geom: str
    end_point_geom: str
    line_start_intersections: dict
    line_end_intersections: dict
    asset_name: str
    asset_label: str
    line_junctions: List[LineJunctionModel]
    intersect_points: List[IntersectPointModel]
    attributes: Dict[str, Any] = Field(default_factory=dict)

    # See the following properties to obtain shapely objects:
    # - line_geom_shapely
    # - start_point_geom_shapely
    # - end_point_geom_shapely

    def __repr__(self):
        base = super().__repr__()
        return f"{base}, line_geom_shapely={self.line_geom_shapely.wkt!r}, start_point_geom_shapely={self.start_point_geom_shapely.wkt!r}, end_point_geom_shapely={self.end_point_geom_shapely.wkt!r}"

    @property
    def line_geom_shapely(self) -> BaseGeometry:
        clean_hex = self.line_geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @property
    def start_point_geom_shapely(self) -> BaseGeometry:
        clean_hex = self.start_point_geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @property
    def end_point_geom_shapely(self) -> BaseGeometry:
        clean_hex = self.end_point_geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @field_validator("line_geom", mode="after")
    @classmethod
    def validate_linestring_geometry(cls, value: str) -> str:
        return super().validate_linestring_geometry(value)

    @field_validator("start_point_geom", "end_point_geom", mode="after")
    @classmethod
    def validate_point_geometry(cls, value: str) -> str:
        return super().validate_point_geometry(value)

    @model_validator(mode="before")
    @classmethod
    def collect_attributes(cls, values):
        defined_keys = cls.__fields__.keys()
        attribute_fields = {k: v for k, v in values.items() if k not in defined_keys}
        values["attributes"] = attribute_fields
        return values


class GeoTransformListModel(RootModel[List[GeoTransformModel]]):
    pass
