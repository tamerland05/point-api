from datetime import datetime
from uuid import UUID

from pydantic import Field

from point_shared.entity_types import Image, PointHash
from point_shared.view import PointBase


class PurposeIconCreateIn(PointBase):
    preview_hash: PointHash
    icon_hash: PointHash


class PurposeIconUpdateIn(PointBase):
    preview_hash: PointHash | None = Field(default=None)
    icon_hash: PointHash | None = Field(default=None)
    enabled: bool | None = Field(default=None)


class PurposeIconAdminOut(PointBase):
    id: UUID
    preview: Image
    icon: Image
    enabled: bool
    created_at: datetime
    updated_at: datetime
