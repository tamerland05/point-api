from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks

from point.controllers import UserController
from point.errors import APIException, ErrorCode
from point.view import AuthIn, AuthOut, AuthUserOut

from point.auth import create_token, validate_telegram_init_data

router = APIRouter()


@router.post("")
async def post_auth(auth_data: AuthIn, background_tasks: BackgroundTasks) -> AuthOut:
    if not validate_telegram_init_data(auth_data):
        raise APIException(ErrorCode.WRONG_CREDENTIALS)

    payload = {
        "iss": uuid4().hex,
        "id": str(auth_data.user.id),
    }

    access_token = create_token(payload)

    user, created = await UserController.get_or_create_user(user_in=auth_data.user)
    if not created:
        async def background_update():
            await user.update_from_dict(auth_data.user.model_dump(mode="json")).save()
        background_tasks.add_task(background_update)

    return AuthOut(access_token=access_token, user=AuthUserOut.model_validate(user))
