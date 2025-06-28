from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import User
from point.view import AuthUserIn


class UserController(BaseController[User]):
    error_code: ErrorCode = ErrorCode.USER_NOT_FOUND
    model = User

    @classmethod
    async def get_or_create_user(cls, user_in: AuthUserIn) -> (model, bool):
        user = await cls.get_or_none(id=user_in.id, enabled=True)
        created = False

        if user is None:
            user = await UserController.create(model_create_in=user_in)
            created = True

        return user, created

    @classmethod
    async def get_user(cls, user_id: int) -> model:
        user = await cls.get("employee", id=user_id, enabled=True)

        if user.employee_id is None:
            user.employee = None

        return user

    @classmethod
    async def get_by_employee(cls, employee_id: UUID) -> model:
        return await cls.get(employee_id=employee_id, enabled=True)

    @classmethod
    def validate_meta(cls, employee: model) -> None:
        if not employee.meta["show_tips_left"]:
            employee.tips_left = None
