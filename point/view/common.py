from decimal import Decimal

from pydantic import Field

from point.view import PointBase


class PointRequestIn(PointBase):
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)


class PointUploadIn(PointRequestIn):
    address: str = Field(max_length=128)


class PointOut(PointUploadIn):
    pass


class PointWithScale(PointRequestIn):
    scale: Decimal = Field(ge=0)


class Cost(PointBase):
    value: Decimal = Field(ge=0)
    currency: str = Field(max_length=8)
