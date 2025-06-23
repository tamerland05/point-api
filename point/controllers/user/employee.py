from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Employee


class EmployeeController(BaseController[Employee]):
    error_code: ErrorCode = ErrorCode.EMPLOYEE_NOT_FOUND
    model = Employee

    @classmethod
    async def get_employee(cls, employee_id: UUID) -> model:
        return await cls.get(id=employee_id, enabled=True)
