from uuid import UUID

from pydantic import Field

from point.entity_types import Image
from point.view import PointBase, Cost


class MenuItemOut(PointBase):
    id: UUID
    establishment_id: UUID
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    photo: Image
    cost: Cost
