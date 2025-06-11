from decimal import Decimal
from uuid import UUID

from pydantic import Field

from point.entity_types import Image, TonAddress
from point.view import PointBase


class AssetOut(PointBase):
    id: UUID
    name: str = Field(max_length=32)
    ticker: str = Field(max_length=16)
    price: Decimal = Field(default=0)
    address: TonAddress
    icon: Image
