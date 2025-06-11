from uuid import UUID

from pydantic import Field

from point.entity_types import Image
from point.view import PointBase


class EstablishmentTypeOut(PointBase):
    id: UUID
    name: str = Field(max_length=128)
    icon: Image
