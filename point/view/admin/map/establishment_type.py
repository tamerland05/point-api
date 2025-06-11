from pydantic import Field

from point.entity_types import PointHash
from point.view import PointBase


class EstablishmentTypeCreateIn(PointBase):
    name: str = Field(max_length=128)
    icon_hash: PointHash


class EstablishmentTypeUpdateIn(PointBase):
    name: str | None = Field(max_length=128, default=None)
    icon_hash: PointHash | None = None
