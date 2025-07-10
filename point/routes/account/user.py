from fastapi import Depends, APIRouter

from point.auth import get_user
from point.controllers import UserController, EmployeeController
from point.view import UserUpdateIn, AuthUser, UserPublicOut

router = APIRouter()


@router.get("/{user_id}")
async def get(user_id: int, _: AuthUser = Depends(get_user)) -> UserPublicOut:
    user = await UserController.get_user(user_id=user_id)

    EmployeeController.validate_meta(user.employee)
    UserController.validate_meta(user)

    return UserPublicOut.model_validate(user)


@router.put("")
async def update(update_in: UserUpdateIn, user: AuthUser = Depends(get_user)) -> None:
    await UserController.update("employee", model_update_in=update_in, id=user.id)
