from fastapi import APIRouter, Depends

from point.auth import get_user
from point.controllers import UserController, EmployeeController
from point.view import AuthUser, UserPublicOut

router = APIRouter()


@router.get("")
async def get_top(_: AuthUser = Depends(get_user)) -> list[UserPublicOut]:
    top = await UserController.get_top_users()
    for user in top:
        EmployeeController.validate_meta(user.employee)
    return UserPublicOut.list_validate(top)
