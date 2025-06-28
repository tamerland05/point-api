from pydantic import Field

from point.view import PointBase

from . import AuthUserIn, AuthUserOut


class AuthIn(PointBase):
    hash: str = Field(max_length=256)
    referrer_data: str | None = Field(default=None, max_length=256)
    user: AuthUserIn


class AuthOut(PointBase):
    user: AuthUserOut
    access_token: str
