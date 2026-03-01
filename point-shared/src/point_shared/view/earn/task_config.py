from pydantic import Field

from point_shared.view import PointBase


class TgMembershipConfig(PointBase):
    ids: list[int | str] = Field(default_factory=list, max_length=100)
