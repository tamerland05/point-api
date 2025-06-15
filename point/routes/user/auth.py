from uuid import uuid4

from fastapi import APIRouter

from point.errors import APIException
from point.view import (
    AuthIn,
    AuthOut,
    AuthUserOut,
    JobPlaceOut,
    Purpose,
    EmployeeMeta,
    EmployeeOut,
    random_address,
    fake,
)

from point.auth import create_token, validate_telegram_init_data

router = APIRouter()


@router.post("")
async def post_auth(auth_data: AuthIn, is_employee: bool = True) -> AuthOut:
    if not validate_telegram_init_data(auth_data):
        raise APIException("Wrong credentials", 401)

    payload = {
        "iss": uuid4().hex,
        "username": auth_data.user.username,
        "id": str(auth_data.user.id),
    }

    access_token = create_token(payload)

    user_out = AuthUserOut(
        **auth_data.user.model_dump(),
        wallet=random_address(),
        rank=fake.random_int(1, 10 ** 10),
        bonus_balance=fake.random_int(1, 10 ** 10),
        typs_left=fake.random_int(1, 10 ** 10),
        account=EmployeeOut(
            id=uuid4(),
            job_place=JobPlaceOut(
                id=uuid4(),
                name=fake.name(),
                address=fake.address(),
            ),
            purpose=Purpose(
                title=fake.name(),
                description=fake.text(),
                icon=fake.image_url(1280, 720)
            ),
            meta=EmployeeMeta(
                show_job=fake.boolean(),
                show_purpose=fake.boolean(),
            )
        ) if is_employee else None
    )

    return AuthOut(access_token=access_token, user=user_out)
