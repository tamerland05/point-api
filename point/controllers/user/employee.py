from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Employee


class EmployeeController(BaseController[Employee]):
    error_code: ErrorCode = ErrorCode.EMPLOYEE_NOT_FOUND
    model = Employee

    @classmethod
    async def get_employee(cls, employee_id: UUID) -> model:
        return await cls.get("job_place", id=employee_id, enabled=True)

    @classmethod
    def validate_meta(cls, employee: model | None) -> None:
        if employee is None:
            return

        if employee.meta["show_job"]:
            employee.job_place = None

        if not employee.meta["show_purpose"]:
            employee.purpose = None
