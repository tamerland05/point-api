from uuid import uuid4

from fastapi import APIRouter

from point.errors import APIException
from point.types import UserType
from point.view import (
    AuthIn,
    AuthOut,
    AuthUserOut,
    ConsumerOut,
    JobPlaceOut,
    PurposeOut,
    EmployeeMeta,
    EmployeeOut,
    ConsumerMeta,
    random_address,
    fake,
)

from point.auth import create_token, validate_telegram_init_data

router = APIRouter(tags=["Auth"])


@router.post("")
async def post_auth(auth_data: AuthIn, user_type: UserType = UserType.consumer) -> AuthOut:
    if not validate_telegram_init_data(auth_data):
        raise APIException("Wrong credentials", 401)

    payload = {
        "iss": uuid4().hex,
        "username": auth_data.user.username,
        "id": str(auth_data.user.id),
    }

    access_token = create_token(payload)

    user_out = AuthUserOut(
        **auth_data.model_dump(),
        rank=fake.random_int(1, 10 ** 10),
        bonus_balance=fake.random_int(1, 10 ** 10),
        user_type=user_type,
        account=ConsumerOut(
            id=uuid4(),
            typs_left=fake.random_int(1, 10 ** 10),
            wallet=random_address(),
            meta=ConsumerMeta(show_tips_left=fake.boolean())
        ) if user_type == UserType.consumer else EmployeeOut(
            id=uuid4(),
            wallet=random_address(),
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
            ),
            meta=EmployeeMeta(
                show_job=fake.boolean(),
                show_purpose=fake.boolean(),
            )
        )
    )

    return AuthOut(access_token=access_token, user=user_out)
