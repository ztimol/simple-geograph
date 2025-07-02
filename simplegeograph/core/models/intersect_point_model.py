import binascii
from typing import Any, Dict, List
from pydantic import Field, NonNegativeInt, field_validator
from shapely import wkb
from shapely.geometry.base import BaseGeometry
from .base_geo_model import BaseGeoModel


class IntersectPointModel(BaseGeoModel):

    tag: NonNegativeInt
    geom: str
    srid: NonNegativeInt
    asset_name: str
    asset_label: str
    line_touches_tags: List[NonNegativeInt]
    attributes: Dict[str, Any] = Field(default_factory=dict)

    @property
    def geom_shapely(self) -> BaseGeometry:
        clean_hex = self.geom.replace("\\x", "")
        return wkb.loads(binascii.unhexlify(clean_hex))

    @field_validator("geom", mode="after")
    @classmethod
    def validate_point_geometry(cls, value: str) -> str:
        return super().validate_point_geometry(value)
