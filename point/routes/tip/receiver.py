from uuid import UUID

from fastapi import APIRouter

from point.controllers import EmployeeController
from point.view import EmployeeReceiver, ReceiversOut

router = APIRouter()


@router.get("s/{establishment_id}")
async def get_receivers(establishment_id: UUID) -> ReceiversOut:
    employees = await EmployeeController.filter(job_place_id=establishment_id)
    return ReceiversOut(employees=[EmployeeReceiver.model_validate(e) for e in employees])
