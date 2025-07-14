from decimal import Decimal
from uuid import UUID

from pydantic import Field

from point.entity_types import Image, TonAddress
from point.view import PointBase


class AssetOut(PointBase):
    id: UUID
    symbol: str = Field(max_length=16)
    name: str = Field(max_length=32)
    address: TonAddress
    price: Decimal
    image_url: Image


class JettonWalletOut(PointBase):
    address: TonAddress
    balance: int = Field(ge=0)
