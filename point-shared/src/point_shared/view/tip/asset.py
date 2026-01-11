from decimal import Decimal
from uuid import UUID

from pydantic import Field

from point_shared.entity_types import Image, TonAddress
from point_shared.view import PointBase


class AssetOut(PointBase):
    id: UUID
    symbol: str = Field(max_length=16)
    name: str = Field(max_length=32)
    address: TonAddress
    decimals: int
    price: Decimal
    image_url: Image


class JettonWalletOut(PointBase):
    address: TonAddress
    balance: int = Field(ge=0)
