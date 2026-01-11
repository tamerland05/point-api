from uuid import UUID

from pydantic import Field

from point_shared.view import PointBase


class InvitationOut(PointBase):
    establishment_id: UUID
    profession: str = Field(max_length=32)
