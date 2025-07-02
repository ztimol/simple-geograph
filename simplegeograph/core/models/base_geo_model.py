import binascii
from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from shapely import wkb
from shapely.geometry.base import BaseGeometry


class BaseGeoModel(BaseModel):
    """This is an abstract base class"""

    model_config = ConfigDict(strict=True)

    @classmethod
    def validate_linestring_geometry(cls, value: str) -> str:
        try:
            clean_hex = value.replace("\\x", "")
            wkb_bytes = binascii.unhexlify(clean_hex)
            geom = wkb.loads(wkb_bytes)
            if geom.geom_type != "LineString":
                raise ValueError("Geometry is not a LineString.")
            return value
        except Exception as e:
            raise ValueError(f"Invalid geometry string: {e}")

    @classmethod
    def validate_point_geometry(cls, value: str) -> str:
        try:
            clean_hex = value.replace("\\x", "")
            wkb_bytes = binascii.unhexlify(clean_hex)
            geom = wkb.loads(wkb_bytes)
            if geom.geom_type != "Point":
                raise ValueError("Geometry is not a Point.")
            return value
        except Exception as e:
            raise ValueError(f"Invalid geometry string: {e}")

    @model_validator(mode="before")
    @classmethod
    def collect_attributes(cls, values):
        defined_keys = cls.__fields__.keys()
        attribute_fields = {k: v for k, v in values.items() if k not in defined_keys}
        values["attributes"] = attribute_fields
        return values
