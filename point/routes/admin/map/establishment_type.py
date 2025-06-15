from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentTypeController
from point.view import EstablishmentTypeCreateIn, EstablishmentTypeUpdateIn, EstablishmentTypeAdminOut

router = APIRouter()


@router.get("/{establishment_type_id}")
async def get_establishment_type(
        establishment_type_id: UUID,
) -> EstablishmentTypeAdminOut:
    establishment = await EstablishmentTypeController.get(id=establishment_type_id)
    return EstablishmentTypeAdminOut.model_validate(establishment)


@router.post("")
async def create_establishment_type(
        establishment_type_in: EstablishmentTypeCreateIn,
) -> EstablishmentTypeAdminOut:
    establishment = await EstablishmentTypeController.create(establishment_type_in)
    return EstablishmentTypeAdminOut.model_validate(establishment)


@router.put("/{establishment_type_id}")
async def update_establishment_type(
        establishment_type_id: UUID,
        establishment_type_update_in: EstablishmentTypeUpdateIn,
) -> EstablishmentTypeAdminOut:
    establishment = await EstablishmentTypeController.update(
        model_update_in=establishment_type_update_in,
        id=establishment_type_id
    )
    return EstablishmentTypeAdminOut.model_validate(establishment)


@router.delete("/{establishment_type_id}")
async def delete_establishment_type(
        establishment_type_id: UUID,
) -> None:
    await EstablishmentTypeController.delete_by_uuid(model_id=establishment_type_id)
