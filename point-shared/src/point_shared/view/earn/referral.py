from pydantic import Field

from point_shared.entity_types import Image
from point_shared.view import PointBase


class ReferralOut(PointBase):
    name: str = Field(max_length=32)
    bonus_balance: int = 0
    photo_url: Image
