from datetime import datetime
from uuid import UUID

from pydantic import Field

from point.view import PointBase


class InvitationCreateIn(PointBase):
    user_id: int
    establishment_id: UUID
    profession: str = Field(default="waiter", max_length=32)


class InvitationDeleteIn(PointBase):
    user_id: int
    establishment_id: UUID


class InvitationAdminOut(InvitationCreateIn):
    created_at: datetime
    updated_at: datetime
