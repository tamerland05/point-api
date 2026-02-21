from decimal import Decimal, ROUND_HALF_UP

from pydantic import Field, field_validator

from point_shared.entity_types import Image, TonAddress
from point_shared.view import PointBase

from . import EmployeeOut, EmployeePublicOut


class UserMeta(PointBase):
    show_tips_left: bool = False


class AuthUserIn(PointBase):
    id: int
    is_premium: bool = False
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    username: str | None = Field(default=None)
    language_code: str | None = Field(default=None)
    photo_url: Image | None = Field(default=None)


class UserPublicOut(PointBase):
    id: int
    photo_url: Image | None = Field(default=None)
    name: str
    username: str | None = Field(default=None)
    bonus_balance: int = 0
    referrals_bonus_balance: int = 0
    rank: int = Field(ge=0)
    tips_left: Decimal | None = Field(ge=0, default=None)
    employee: EmployeePublicOut | None = Field(default=None)

    @field_validator("tips_left", mode="after")
    def validate_employee(cls, tips_left: Decimal | None) -> Decimal | None:
        if tips_left is None:
            return None
        else:
            return tips_left.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP).normalize()


class AuthUserOut(UserPublicOut):
    wallet: TonAddress | None = Field(default=None)
    tips_left: Decimal = Field(ge=0)
    meta: UserMeta
    employee: EmployeeOut | None = Field(default=None)


class AuthUser(PointBase):
    id: int
    sessionId: str | None = Field(default=None)


class UserUpdateIn(PointBase):
    wallet: TonAddress | None = Field(default=None)
    meta: UserMeta | None = Field(default=None)
