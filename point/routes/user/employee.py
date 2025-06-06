from uuid import UUID, uuid4

from fastapi import APIRouter, Depends

from point.auth import get_user
from point.types import UserType
from point.view import (
    AuthUser,
    UserPublicOut,
    JobPlaceOut,
    EmployeeUpdateIn,
    EmployeePublicOut,
    EmployeeMeta,
    PurposeOut,
    EmployeeOut,
    AuthUserOut,
    fake,
    random_address,
)

router = APIRouter(tags=["Employee"])


@router.get("/{employee_id}")
async def get(employee_id: UUID, _: AuthUser = Depends(get_user)) -> UserPublicOut:
    return UserPublicOut(
        name=fake.name(),
        username=fake.user_name(),
        rank=fake.random_int(1, 10 ** 10),
        user_type=UserType.employee,
        account=EmployeePublicOut(
            id=employee_id,
            job_place=fake.random_element([JobPlaceOut(
                id=uuid4(),
                name=fake.name(),
                address=fake.address(),
            ), None]),
            purpose=fake.random_element([PurposeOut(
                id=uuid4(),
                title=fake.name(),
                description=fake.text(),
                icon=fake.image_url(1280, 720)
            ), None]),
            wallet=random_address(),
        )
    )


@router.put("")
async def update(update_in: EmployeeUpdateIn, user: AuthUser = Depends(get_user)) -> AuthUserOut:
    return AuthUserOut(
        id=user.id,
        username=user.username,
        rank=fake.random_int(1, 10 ** 10),
        bonus_balance=fake.random_int(1, 10 ** 10),
        user_type=UserType.employee,
        account=EmployeeOut(
            id=uuid4(),
            wallet=random_address() if update_in.wallet is None else update_in.wallet,
            job_place=JobPlaceOut(
                id=uuid4(),
                name=fake.name(),
                address=fake.address(),
            ),
            purpose=PurposeOut(
                id=uuid4(),
                title=fake.name(),
                description=fake.text(),
                icon=fake.image_url(1280, 720)
            ) if update_in.purpose is None else update_in.purpose,
            meta=EmployeeMeta(
                show_job=fake.boolean(),
                show_purpose=fake.boolean(),
            ) if update_in.meta is None else update_in.meta
        )
    )
