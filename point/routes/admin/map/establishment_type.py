from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentTypeController
from point.view import EstablishmentTypeOut, EstablishmentTypeCreateIn, EstablishmentTypeUpdateIn

router = APIRouter()


@router.get("/{establishment_type_id}")
async def get_establishment_type(
        establishment_type_id: UUID,
) -> EstablishmentTypeOut:
    establishment = await EstablishmentTypeController.get(id=establishment_type_id)
    return EstablishmentTypeOut.model_validate(establishment)


@router.post("")
async def create_establishment_type(
        establishment_type_in: EstablishmentTypeCreateIn,
) -> EstablishmentTypeOut:
    establishment = await EstablishmentTypeController.create(establishment_type_in)
    return EstablishmentTypeOut.model_validate(establishment)


@router.put("/{establishment_type_id}")
async def update_establishment_type(
        establishment_type_id: UUID,
        establishment_type_update_in: EstablishmentTypeUpdateIn,
) -> EstablishmentTypeOut:
    establishment = await EstablishmentTypeController.update(
        model_update_in=establishment_type_update_in,
        id=establishment_type_id
    )
    return EstablishmentTypeOut.model_validate(establishment)


@router.delete("/{establishment_type_id}")
async def delete_establishment_type(
        establishment_type_id: UUID,
) -> None:
    await EstablishmentTypeController.delete_by_uuid(model_id=establishment_type_id)
