from uuid import UUID

from pydantic import Field

from point.entity_types import Image
from point.view import PointBase


class Creator(PointBase):
    name: str = Field(max_length=32)
    icon: Image


class SelectionPreview(PointBase):
    id: UUID
    creator: Creator
    main_area: str = Field(max_length=32)
    name: str = Field(max_length=64)
    description: str = Field(max_length=256)
    icons: list[Image] = Field(default_factory=list)
    places_count: int = Field(default=0, ge=0)
    preview_places_icons: list[Image] = Field(default_factory=list)


class PlaceItem(PointBase):
    id: UUID
    name: str = Field(max_length=64)
    description: str = Field(max_length=256)
    icon: Image
    address: str = Field(max_length=64)


class SelectionOut(PointBase):
    id: UUID
    creator: Creator
    main_area: str = Field(max_length=32)
    places: list[PlaceItem] = Field(default_factory=list)
