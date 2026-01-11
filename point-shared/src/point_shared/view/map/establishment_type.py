from uuid import UUID

from pydantic import Field

from point_shared.entity_types import Image
from point_shared.view import PointBase


class EstablishmentTypeOut(PointBase):
    id: UUID
    name: str = Field(max_length=128)
    icon: Image
    color_code: str | None = Field(default=None)
