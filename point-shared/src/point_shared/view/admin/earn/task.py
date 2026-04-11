from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field, AnyUrl

from point_shared.entity_types import PointHash, TaskIntegrationType
from point_shared.view import PointBase


class TaskCreateIn(PointBase):
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    profit: int = Field(ge=0)
    icon_hash: PointHash
    link: AnyUrl = Field(max_length=1024)
    integration_type: TaskIntegrationType
    config: Any = Field(default=None)


class TaskUpdateIn(PointBase):
    title: str | None = Field(max_length=128, default=None)
    description: str | None = Field(max_length=512, default=None)
    profit: int | None = Field(ge=0, default=None)
    icon_hash: PointHash | None = Field(default=None)
    link: AnyUrl | None = Field(max_length=1024, default=None)
    integration_type: TaskIntegrationType | None = Field(default=None)
    enabled: bool | None = Field(default=None)
    config: Any = Field(default=None)


class TaskAdminOut(PointBase):
    id: UUID
    title: str = Field(max_length=128)
    description: str = Field(max_length=512)
    profit: int = Field(ge=0)
    icon_hash: PointHash
    link: AnyUrl = Field(max_length=1024)
    integration_type: TaskIntegrationType
    config: Any = Field(None)
    enabled: bool
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(default=None)
