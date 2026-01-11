from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentTypeController
from point.view import EstablishmentTypeCreateIn, EstablishmentTypeUpdateIn, EstablishmentTypeAdminOut

router = APIRouter()


@router.get("/{establishment_type_id}")
async def get_establishment_type(
        establishment_type_id: UUID,
) -> EstablishmentTypeAdminOut:
    establishment_type = await EstablishmentTypeController.get(id=establishment_type_id)
    return EstablishmentTypeAdminOut.model_validate(establishment_type)


@router.get("s")
async def get_all_establishment_types() -> list[EstablishmentTypeAdminOut]:
    establishment_types = await EstablishmentTypeController.filter()
    return EstablishmentTypeAdminOut.list_validate(establishment_types)


@router.post("")
async def create_establishment_type(
        establishment_type_in: EstablishmentTypeCreateIn,
) -> EstablishmentTypeAdminOut:
    establishment_type = await EstablishmentTypeController.create(establishment_type_in)
    return EstablishmentTypeAdminOut.model_validate(establishment_type)


@router.put("/{establishment_type_id}")
async def update_establishment_type(
        establishment_type_id: UUID,
        establishment_type_update_in: EstablishmentTypeUpdateIn,
) -> EstablishmentTypeAdminOut:
    establishment_type = await EstablishmentTypeController.update(
        model_update_in=establishment_type_update_in,
        id=establishment_type_id
    )
    return EstablishmentTypeAdminOut.model_validate(establishment_type)


@router.delete("/{establishment_type_id}")
async def delete_establishment_type(
        establishment_type_id: UUID,
) -> None:
    await EstablishmentTypeController.delete(id=establishment_type_id)
