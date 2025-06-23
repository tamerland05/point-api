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
        user = await cls.get_or_none("employee", id=user_in.id, enabled=True)
        created = False

        if user is None:
            user = await UserController.create(model_create_in=user_in)
            created = True

        if user.employee_id is not None:
            await user.employee.fetch_related("job_place")
        else:
            user.employee = None

        return user, created

    @classmethod
    async def get_user(cls, user_id: int) -> model:
        return await cls.get(id=user_id, enabled=True)

    @classmethod
    async def get_by_employee(cls, employee_id: UUID) -> model:
        return await cls.get(employee_id=employee_id, enabled=True)
