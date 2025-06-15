from datetime import datetime

from pydantic import Field

from point.entity_types import PointHash
from point.view import PointBase, EstablishmentTypeOut


class EstablishmentTypeCreateIn(PointBase):
    name: str = Field(max_length=128)
    icon_hash: PointHash


class EstablishmentTypeUpdateIn(PointBase):
    name: str | None = Field(max_length=128, default=None)
    icon_hash: PointHash | None = None
    enabled: bool | None = None


class EstablishmentTypeAdminOut(EstablishmentTypeOut):
    enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
