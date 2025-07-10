from math import ceil

from fastapi import APIRouter, Depends, Query
from fastapi_pagination import Page

from point.auth import get_user
from point.controllers import UserController
from point.view import AuthUser, ReferralOut

router = APIRouter()


@router.get("s")
async def get_referrals(
        user: AuthUser = Depends(get_user),
        page: int = Query(ge=1, default=1),
        size: int = Query(ge=1, le=100, default=10)
) -> Page[ReferralOut]:
    total_rows = await UserController.count_referrals(referrer_id=user.id)
    total_pages = ceil(total_rows / size)
    referrals = await UserController.find_referrals(referrer_id=user.id, page=page, size=size)
    return Page(total=total_rows, page=page, size=size, items=ReferralOut.list_validate(referrals), pages=total_pages)
