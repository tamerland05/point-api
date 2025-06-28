from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentController, EstablishmentTypeController
from point.view import (
    EstablishmentCreateIn,
    EstablishmentUpdateIn,
    EstablishmentDbCreateIn,
    EstablishmentAdminOut,
)

router = APIRouter()


@router.get("/{establishment_id}")
async def get_establishment(
        establishment_id: UUID,
) -> EstablishmentAdminOut:
    establishment = await EstablishmentController.get_establishment(establishment_id=establishment_id)
    return EstablishmentAdminOut.model_validate(establishment)


@router.get("s")
async def get_all_establishments() -> list[EstablishmentAdminOut]:
    establishments = await EstablishmentController.filter()
    return [EstablishmentAdminOut.model_validate(e) for e in establishments]


@router.post("")
async def create_establishment(
        establishment_in: EstablishmentCreateIn,
) -> EstablishmentAdminOut:
    await EstablishmentTypeController.get(id=establishment_in.establishment_type_id)

    establishment_in = EstablishmentDbCreateIn(
        **establishment_in.model_dump(),
        **establishment_in.position.model_dump(),
    )
    establishment = await EstablishmentController.admin_create(establishment_in)
    return EstablishmentAdminOut.model_validate(establishment)


@router.put("/{establishment_id}")
async def update_establishment(
        establishment_id: UUID,
        establishment_update_in: EstablishmentUpdateIn,
) -> EstablishmentAdminOut:
    if establishment_update_in.establishment_type_id is not None:
        await EstablishmentTypeController.get(id=establishment_update_in.establishment_type_id)

    establishment = await EstablishmentController.update(
        "menu",
        model_update_in=establishment_update_in,
        id=establishment_id
    )
    return EstablishmentAdminOut.model_validate(establishment)


@router.delete("/{establishment_id}")
async def delete_establishment(
        establishment_id: UUID,
) -> None:
    await EstablishmentController.delete_by_uuid(model_id=establishment_id)
