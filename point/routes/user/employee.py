from uuid import UUID, uuid4

from fastapi import APIRouter, Depends

from point.auth import get_user
from point.view import (
    AuthUser,
    UserPublicOut,
    JobPlaceOut,
    EmployeeUpdateIn,
    EmployeePublicOut,
    Purpose,
    fake,
)

router = APIRouter(tags=["Employee"])


@router.get("/{employee_id}")
async def get(employee_id: UUID, _: AuthUser = Depends(get_user)) -> UserPublicOut:
    return UserPublicOut(
        name=fake.name(),
        username=fake.user_name(),
        rank=fake.random_int(1, 10 ** 10),
        typs_left=fake.random_int(1, 10 ** 10),
        account=EmployeePublicOut(
            id=employee_id,
            job_place=fake.random_element([JobPlaceOut(
                id=uuid4(),
                name=fake.name(),
                address=fake.address(),
            ), None]),
            purpose=fake.random_element([Purpose(
                title=fake.name(),
                description=fake.text(),
                icon=fake.image_url(1280, 720)
            ), None]),
        )
    )


@router.put("")
async def update(update_in: EmployeeUpdateIn, user: AuthUser = Depends(get_user)) -> None:
    return None
