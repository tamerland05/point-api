from uuid import UUID

from pydantic import Field

from point_shared.entity_types import Image
from point_shared.view import PointBase


class PurposeIconOut(PointBase):
    id: UUID
    preview: Image


class Purpose(PointBase):
    icon: Image
    title: str = Field(max_length=32)
    description: str = Field(max_length=512)


class PurposeIn(PointBase):
    icon: str
    title: str = Field(max_length=32)
    description: str = Field(max_length=512)
