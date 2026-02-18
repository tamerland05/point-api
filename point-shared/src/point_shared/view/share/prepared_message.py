from pydantic import Field

from point_shared.view import PointBase


class PreparedMessage(PointBase):
    id: str = Field(max_length=64)
