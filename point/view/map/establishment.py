from decimal import Decimal
from uuid import UUID

from pydantic import Field, AnyUrl

from point.entity_types import Image
from point.view import PointBase, PointOut, PointRequestIn

from .menu_item import MenuItemOut


class EstablishmentPreview(PointBase):
    id: UUID
    name: str = Field(max_length=128)
    photo: Image
    establishment_type_id: UUID
    position: PointOut
    rating: Decimal = Field(ge=0)


class NearEstablishmentCriteria(PointBase):
    name: str | None = Field(max_length=128)
    location: PointRequestIn


class EstablishmentOut(EstablishmentPreview):
    description: str = Field(max_length=512)
    user_rating: int | None = Field(default=None, ge=0, le=5)
    channel_link: AnyUrl | None = Field(default=None, max_length=512)
    icon: Image
    gallery: list[Image] = Field(default_factory=list)
    menu: list[MenuItemOut] = Field(default_factory=list)
