import asyncio
import json

from fastapi import APIRouter, Depends
from starlette.requests import Request
from tortoise.transactions import in_transaction

from point.auth import get_user
from point.controllers import EmployeeController, PurposeIconController, UserController, InvitationController
from point.entity_types import PointHash
from point.services import storage
from point.view import AuthUser, EmployeeCreateIn, EmployeeDbCreateIn, EmployeeUpdateIn, EmployeeDbUpdateIn

router = APIRouter()


@router.post("")
async def create(request: Request, user: AuthUser = Depends(get_user)) -> None:
    user, invitation, form = await asyncio.gather(
        UserController.get_user(user_id=user.id),
        InvitationController.get(user_id=user.id),
        request.form(),
    )

    create_in = EmployeeCreateIn.model_validate(json.loads(form.get("update_in")))

    photo = form.get("file")
    photo_hash, purpose_icon = await asyncio.gather(
        storage.put_file(filename=photo.filename, data=await photo.read()),
        PurposeIconController.get(id=create_in.purpose.icon),
    )

    create_in.purpose.icon = purpose_icon.icon
    create_in = EmployeeDbCreateIn(
        job_place_id=invitation.establishment_id,
        profession=invitation.profession,
        photo_hash=photo_hash,
        **create_in.model_dump()
    )

    async with in_transaction():
        employee = await EmployeeController.create(model_create_in=create_in)
        user.employee_id = employee.id
        await asyncio.gather(
            user.save(update_fields=["employee_id"]),
            invitation.delete()
        )


@router.put("")
async def update(request: Request, user: AuthUser = Depends(get_user)) -> None:
    user = await UserController.get_user(user_id=user.id)

    form = await request.form()
    update_in = EmployeeDbUpdateIn(
        **EmployeeUpdateIn.model_validate(
            json.loads(form.get("update_in", "{}"))
        ).model_dump(exclude_unset=True)
    )
    photo = form.get("file")

    if photo is not None:
        update_in.photo_hash = PointHash(root=await storage.put_file(filename=photo.filename, data=await photo.read()))

    if update_in.purpose is not None:
        purpose_icon = await PurposeIconController.get(id=update_in.purpose.icon)
        update_in.purpose.icon = purpose_icon.icon

    await EmployeeController.update(id=user.employee_id, model_update_in=update_in)


@router.delete("")
async def delete(user: AuthUser = Depends(get_user)) -> None:
    user = await UserController.get_user(user_id=user.id)
    employee = user.employee

    user.employee_id = None
    employee.enabled = False

    async with in_transaction():
        await asyncio.gather(
            user.save(update_fields=["employee_id"]),
            employee.save(update_fields=["enabled"]),
        )
