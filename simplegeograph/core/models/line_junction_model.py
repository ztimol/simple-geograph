import binascii
from typing import Any, Dict, List
from pydantic import Field, ConfigDict, NonNegativeInt, field_validator
from shapely import wkb
from shapely.geometry.base import BaseGeometry
from .base_geo_model import BaseGeoModel


class LineJunctionModel(BaseGeoModel):

    tag: NonNegativeInt
    geom: str
    asset_name: str
    asset_label: str
    start_point_geom: str
    end_point_geom: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

    @property
    def geom_shapely(self) -> BaseGeometry:
        clean_hex = self.geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @property
    def start_point_geom_shapely(self) -> BaseGeometry:
        clean_hex = self.start_point_geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @property
    def end_point_geom_shapely(self) -> BaseGeometry:
        clean_hex = self.end_point_geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @field_validator("geom", mode="after")
    @classmethod
    def validate_linestring_geometry(cls, value: str) -> str:
        return super().validate_linestring_geometry(value)

    @field_validator("start_point_geom", "end_point_geom", mode="after")
    @classmethod
    def validate_point_geometry(cls, value: str) -> str:
        return super().validate_point_geometry(value)
