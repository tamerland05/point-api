import struct
from decimal import Decimal

from tortoise.fields import Field, TextField, BigIntField, SmallIntField, IntField

from point.entity_types import TonAddress


class ScaledDecimalField(Field):
    multiplier = Decimal("1e32")

    def __init__(self, multiplier: int | None = None, **kwargs):
        super().__init__(**kwargs)
        if multiplier is not None:
            self.multiplier = Decimal(f"1e{multiplier}")

    def to_db_value(self, value: int | float | Decimal | None, instance) -> int | None:
        if value is None:
            return None
        return int(value * self.multiplier)

    def to_python_value(self, value: int) -> Decimal | None:
        if value is None:
            return None
        return value / self.multiplier


class BigIntDecimalField(ScaledDecimalField, BigIntField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class IntDecimalField(ScaledDecimalField, IntField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SmallIntDecimalField(ScaledDecimalField, SmallIntField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TonAddressField(TextField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_db_value(self, value: TonAddress | None, instance) -> str | None:
        if value is None:
            return None
        return value.root

    def to_python_value(self, value: str) -> TonAddress | None:
        if value is None:
            return None
        return TonAddress(root=value)


class GeographyPointField(Field):
    SQL_TYPE = "geography(Point, 4326)"

    def to_db_value(self, value: tuple[Decimal, Decimal], instance) -> str:
        lon, lat = value
        return f"SRID=4326;POINT({lon} {lat})"

    def to_python_value(self, value: str | tuple[Decimal, Decimal]) -> tuple[Decimal, Decimal]:
        if isinstance(value, tuple | list) and len(value) == 2:
            return value

        wkb_bytes = bytes.fromhex(value)

        endian = wkb_bytes[0]
        byte_order = "<" if endian == 1 else ">"

        geom_type_with_flags = struct.unpack(byte_order + "I", wkb_bytes[1:5])[0]
        geom_type = geom_type_with_flags & 0xFF

        if geom_type != 1:
            raise ValueError(f"Unsupported geometry type: {geom_type}")

        offset = 5
        if has_srid := bool(geom_type_with_flags & 0x20000000):
            offset += 4

        lon = struct.unpack(byte_order + "d", wkb_bytes[offset:offset+8])[0]
        lat = struct.unpack(byte_order + "d", wkb_bytes[offset+8:offset+16])[0]

        return Decimal(str(lon)), Decimal(str(lat))
