from fastapi import Depends

from point.auth import get_user
from point.view import UserUpdateIn, AuthUser
from . import router


@router.put("")
async def update(update_in: UserUpdateIn, user: AuthUser = Depends(get_user)) -> None:
    return None
