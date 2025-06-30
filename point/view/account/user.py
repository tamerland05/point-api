from pydantic import Field

from point.entity_types import Image, TonAddress
from point.view import PointBase

from . import EmployeeOut, EmployeePublicOut


class UserMeta(PointBase):
    show_tips_left: bool = False


class AuthUserIn(PointBase):
    id: int
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    username: str | None = Field(default=None)
    language_code: str | None = Field(default=None)
    photo_url: Image | None = Field(default=None)


class AuthUserOut(AuthUserIn):
    wallet: TonAddress | None = Field(default=None)
    rank: int | None = Field(default=None)
    bonus_balance: int = 0
    tips_left: int = Field(ge=0)
    meta: UserMeta
    employee: EmployeeOut | None = Field(default=None)


class AuthUser(PointBase):
    id: int
    sessionId: str | None = Field(default=None)


class UserPublicOut(PointBase):
    photo_url: Image | None = Field(default=None)
    wallet: TonAddress | None = Field(default=None)
    name: str
    username: str
    rank: int | None = Field(default=None)  # todo: calculate rank
    tips_left: int | None = Field(ge=0, default=None)
    employee: EmployeePublicOut | None = Field(default=None)


class UserUpdateIn(PointBase):
    wallet: TonAddress | None = Field(default=None)
    meta: UserMeta | None = Field(default=None)
