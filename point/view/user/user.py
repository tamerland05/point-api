from pydantic import Field

from point.entity_types import Image, TonAddress
from point.view import PointBase

from . import EmployeeOut, EmployeePublicOut


class UserMeta(PointBase):
    show_tips_left: bool = False


class AuthUserIn(PointBase):
    id: int
    first_name: str = Field(default="")
    last_name: str = Field(default="")
    username: str = Field(default="")
    language_code: str | None = None
    photo_url: Image | None = None
    is_bot: bool = False
    is_premium: bool = False
    allows_write_to_pm: bool = False


class AuthUserOut(AuthUserIn):
    wallet: TonAddress | None = None
    rank: int
    bonus_balance: int = 0
    typs_left: int = Field(ge=0)
    account: EmployeeOut | None = None


class AuthUser(PointBase):
    id: int
    sessionId: str | None = None


class UserPublicOut(PointBase):
    name: str
    username: str
    rank: int
    typs_left: int | None = Field(ge=0, default=None)
    account: EmployeePublicOut | None = None


class UserUpdateIn(PointBase):
    wallet: TonAddress | None = None
    meta: UserMeta | None = None
