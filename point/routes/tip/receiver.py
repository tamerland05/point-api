from uuid import UUID

from fastapi import APIRouter

from point.controllers import EmployeeController, UserController
from point.view import EmployeeReceiver, ReceiversOut

router = APIRouter()


@router.get("s/{establishment_id}")
async def get_receivers(establishment_id: UUID) -> ReceiversOut:
    employees = await EmployeeController.filter(job_place_id=establishment_id)

    # todo: remove this shit
    related_users = dict(await UserController.find_by_employee_ids([e.id for e in employees]))
    for employee in employees:
        employee.id = related_users[employee.id]

    return ReceiversOut(employees=EmployeeReceiver.list_validate(employees))
