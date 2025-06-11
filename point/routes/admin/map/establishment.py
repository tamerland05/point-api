from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentController, EstablishmentTypeController
from point.view import (
    EstablishmentOut,
    EstablishmentCreateIn,
    EstablishmentUpdateIn,
    EstablishmentDbCreateIn
)

router = APIRouter()


@router.get("/{establishment_id}")
async def get_establishment(
        establishment_id: UUID,
) -> EstablishmentOut:
    establishment = await EstablishmentController.get_establishment(establishment_id=establishment_id)
    return EstablishmentOut.model_validate(establishment)


@router.post("")
async def create_establishment(
        establishment_in: EstablishmentCreateIn,
) -> EstablishmentOut:
    await EstablishmentTypeController.get(id=establishment_in.establishment_type_id)

    establishment_in = EstablishmentDbCreateIn(
        **establishment_in.model_dump(),
        **establishment_in.position.model_dump(),
    )
    establishment = await EstablishmentController.create(establishment_in)
    await establishment.fetch_related("menu")

    return EstablishmentOut.model_validate(establishment)


@router.put("/{establishment_id}")
async def update_establishment(
        establishment_id: UUID,
        establishment_update_in: EstablishmentUpdateIn,
) -> EstablishmentOut:
    if establishment_update_in.establishment_type_id is not None:
        await EstablishmentTypeController.get(id=establishment_update_in.establishment_type_id)

    establishment = await EstablishmentController.update(
        "menu",
        model_update_in=establishment_update_in,
        id=establishment_id
    )
    return EstablishmentOut.model_validate(establishment)


@router.delete("/{establishment_id}")
async def delete_establishment(
        establishment_id: UUID,
) -> None:
    await EstablishmentController.delete_by_uuid(model_id=establishment_id)
