from decimal import Decimal
from typing import Self

from pydantic import Field

from point_shared.view import PointBase


class PointRequestIn(PointBase):
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)

    def distance(self, other: Self) -> Decimal:
        return (
                (self.latitude - other.latitude) ** 2 +
                (self.longitude - other.longitude) ** 2
        ).sqrt()


class PointOut(PointRequestIn):
    address: str = Field(max_length=128)


class ViewPortSize(PointBase):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class PointWithScale(PointRequestIn):
    scale: float = Field(ge=0, le=22)
    view_port_size: ViewPortSize


class Cost(PointBase):
    amount: Decimal = Field(ge=0)
    currency: str = Field(max_length=8)
