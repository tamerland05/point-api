from decimal import Decimal
from uuid import UUID

from pydantic import Field

from point.entity_types import PointHash, Image
from point.view import PointBase, Cost


class MenuItemCreateIn(PointBase):
    establishment_id: UUID
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    photo_hash: PointHash | None = Field(default=None)
    cost: Cost


class MenuItemDbCreateIn(MenuItemCreateIn):
    amount: Decimal = Field(ge=0)
    currency: str = Field(max_length=8)


class MenuItemUpdateIn(PointBase):
    establishment_id: UUID | None = Field(default=None)
    title: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    photo_hash: PointHash | None = Field(default=None)
    amount: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=8)
    enabled: bool | None = Field(default=None)


class MenuItemAdminOut(PointBase):
    id: UUID
    establishment_id: UUID
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    photo: Image | None = Field(default=None)
    cost: Cost
    enabled: bool
