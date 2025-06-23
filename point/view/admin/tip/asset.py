from datetime import datetime
from uuid import UUID

from pydantic import Field

from point.view import PointBase


class AssetCreateIn(PointBase):
    symbol: str = Field(max_length=16)
    name: str = Field(max_length=128)
    decimals: int
    address: str = Field(max_length=128)
    image_url: str = Field(max_length=1024)


class AssetUpdateIn(PointBase):
    symbol: str | None = Field(default=None, max_length=16)
    name: str | None = Field(default=None, max_length=128)
    decimals: int | None = Field(default=None)
    address: str | None = Field(default=None, max_length=128)
    image_url: str | None = Field(default=None, max_length=1024)


class AssetAdminOut(AssetCreateIn):
    id: UUID
    ton_price: int
    enabled: bool
    created_at: datetime
    updated_at: datetime
