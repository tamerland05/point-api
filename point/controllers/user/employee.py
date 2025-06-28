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
    async def validate_meta(cls, employee: model) -> None:
        if employee.meta["show_job"]:
            await employee.fetch_related("job_place")
        else:
            employee.job_place = None

        if not employee.meta["show_purpose"]:
            employee.purpose = None
