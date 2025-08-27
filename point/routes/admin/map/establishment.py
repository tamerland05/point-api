from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentController, EstablishmentTypeController
from point.view import EstablishmentCreateIn, EstablishmentUpdateIn, EstablishmentAdminOut

router = APIRouter()


@router.get("/{establishment_id}")
async def get_establishment(
        establishment_id: UUID,
) -> EstablishmentAdminOut:
    establishment = await EstablishmentController.get("menu", id=establishment_id)
    return EstablishmentAdminOut.model_validate(establishment)


@router.get("s")
async def get_all_establishments() -> list[EstablishmentAdminOut]:
    establishments = await EstablishmentController.filter("menu")
    return EstablishmentAdminOut.list_validate(establishments)


@router.post("")
async def create_establishment(
        establishment_in: EstablishmentCreateIn,
) -> EstablishmentAdminOut:
    await EstablishmentTypeController.get(id=establishment_in.establishment_type_id)
    establishment = await EstablishmentController.admin_create(establishment_in)
    return EstablishmentAdminOut.model_validate(establishment)


@router.put("/{establishment_id}")
async def update_establishment(
        establishment_id: UUID,
        establishment_update_in: EstablishmentUpdateIn,
) -> EstablishmentAdminOut:
    if establishment_update_in.establishment_type_id is not None:
        await EstablishmentTypeController.get(id=establishment_update_in.establishment_type_id)

    establishment = await EstablishmentController.get("menu", id=establishment_id)

    model_update_in = establishment_update_in.model_dump(exclude_unset=True)
    model_update_in["location"] = (
        establishment_update_in.longitude if "longitude" in model_update_in else establishment.location.longitude,
        establishment_update_in.latitude if "latitude" in model_update_in else establishment.location.latitude,
    )
    if "longitude" in model_update_in:
        del model_update_in["longitude"]
    if "latitude" in model_update_in:
        del model_update_in["latitude"]

    await (
        establishment
        .update_from_dict(model_update_in)
        .save(update_fields=list(model_update_in.keys()) + ["updated_at"])
    )
    return EstablishmentAdminOut.model_validate(establishment)


@router.delete("/{establishment_id}")
async def delete_establishment(
        establishment_id: UUID,
) -> None:
    await EstablishmentController.delete(id=establishment_id)
