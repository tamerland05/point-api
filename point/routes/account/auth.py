from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks

from point.controllers import UserController, EmployeeController
from point.errors import APIException, ErrorCode
from point.view import AuthIn, AuthOut, AuthUserOut

from point.auth import create_token, validate_telegram_init_data

router = APIRouter()


@router.post("")
async def post_auth(auth_data: AuthIn, background_tasks: BackgroundTasks) -> AuthOut:
    if not validate_telegram_init_data(auth_data):
        raise APIException(ErrorCode.WRONG_CREDENTIALS)

    user, created = await UserController.get_or_create_user(user_in=auth_data.user)
    user_dct = auth_data.user.model_dump(mode="json")
    if not created and any(getattr(user, field) != new for field, new in user_dct.items() if hasattr(user, field)):
        background_tasks.add_task(func=user.update_from_dict(user_dct).save)
    elif auth_data.referrer_id is not None:
        background_tasks.add_task(
            func=UserController.create_referral,
            referrer_id=auth_data.referrer_id,
            user_id=user.id,
            is_premium=auth_data.user.is_premium,
        )

    if user.employee_id is None:
        user.employee = None
    else:
        user.employee = await EmployeeController.get_employee(employee_id=user.employee_id)

    payload = {
        "iss": uuid4().hex,
        "id": str(user.id),
    }

    access_token = create_token(data=payload)

    return AuthOut(access_token=access_token, user=AuthUserOut.model_validate(user))
