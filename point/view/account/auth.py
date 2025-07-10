from pydantic import Field

from point.view import PointBase

from . import AuthUserIn, AuthUserOut


class AuthIn(PointBase):
    hash: str = Field(max_length=256)
    referrer_id: int | None = Field(default=None, ge=0)
    user: AuthUserIn


class AuthOut(PointBase):
    user: AuthUserOut
    access_token: str
