from uuid import UUID

from fastapi import APIRouter

from point.controllers import EmployeeController
from point.view import EmployeeReceiver, ReceiversOut

router = APIRouter()


@router.get("s/{establishment_id}")
async def get_receivers(establishment_id: UUID) -> ReceiversOut:
    employees = await EmployeeController.filter("user", job_place_id=establishment_id, enabled=True)
    filtered_employees = []

    # todo: remove this shit
    for employee in employees:
        if len(employee.user) != 1:
            continue
        employee.id = employee.user[0].id
        filtered_employees.append(employee)

    return ReceiversOut(employees=EmployeeReceiver.list_validate(filtered_employees))
