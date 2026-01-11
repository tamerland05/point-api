from datetime import datetime
from uuid import UUID

from pydantic import Field

from point_shared.entity_types import Image
from point_shared.view import PointBase


class AssetCreateIn(PointBase):
    symbol: str = Field(max_length=16)
    name: str = Field(max_length=128)
    decimals: int
    address: str = Field(max_length=128)
    image_url: Image
    priority: int


class AssetUpdateIn(PointBase):
    symbol: str | None = Field(default=None, max_length=16)
    name: str | None = Field(default=None, max_length=128)
    decimals: int | None = Field(default=None)
    address: str | None = Field(default=None, max_length=128)
    image_url: Image | None = Field(default=None)
    priority: int | None = Field(default=None)
    enabled: bool | None = Field(default=None)


class AssetAdminOut(AssetCreateIn):
    id: UUID
    price: int
    enabled: bool
    created_at: datetime
    updated_at: datetime
