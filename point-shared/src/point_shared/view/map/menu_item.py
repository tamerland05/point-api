from uuid import UUID

from pydantic import Field

from point_shared.entity_types import Image
from point_shared.view import PointBase, Cost


class MenuItemOut(PointBase):
    id: UUID
    establishment_id: UUID
    category: str = Field(max_length=32)
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    photo: Image | None = Field(default=None)
    cost: Cost
