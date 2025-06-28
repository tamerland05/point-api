import json

from fastapi import APIRouter, Depends
from starlette.requests import Request

from point.auth import get_user
from point.controllers import EmployeeController, PurposeIconController, UserController
from point.entity_types import PointHash
from point.services import storage
from point.view import AuthUser, EmployeeUpdateIn, EmployeeDbUpdateIn

router = APIRouter()


@router.put("")
async def update(request: Request, user: AuthUser = Depends(get_user)) -> None:
    user = await UserController.get_user(user_id=user.id)

    form = await request.form()
    update_in = EmployeeDbUpdateIn(
        **EmployeeUpdateIn.model_validate(
            json.loads(form.get("update_in", "{}"))
        ).model_dump()
    )
    photo = form.get("file")

    if photo is not None:
        update_in.photo_hash = PointHash(root=await storage.put_file(filename=photo.filename, data=await photo.read()))

    if update_in.purpose is not None:
        purpose_icon = await PurposeIconController.get(id=update_in.purpose.icon)
        update_in.purpose.icon = purpose_icon.icon

    await EmployeeController.update(id=user.employee_id, model_update_in=update_in)
