from pydantic import Field

from point.view import PointBase

from . import AuthUserOut


class AuthIn(PointBase):
    referrer_id: int | None = Field(default=None, ge=0)
    init_data_raw: str


class AuthOut(PointBase):
    user: AuthUserOut
    access_token: str
