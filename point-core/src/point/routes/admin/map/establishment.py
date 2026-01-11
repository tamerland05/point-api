from math import ceil
from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page
from tortoise.expressions import RawSQL

from point.controllers import EstablishmentController, EstablishmentTypeController
from point.view import EstablishmentCreateIn, EstablishmentUpdateIn, EstablishmentAdminOut, EstablishmentCriteria

router = APIRouter()


@router.get("/{establishment_id}")
async def get_establishment(
        establishment_id: UUID,
) -> EstablishmentAdminOut:
    establishment = await EstablishmentController.get("menu", id=establishment_id)
    return EstablishmentAdminOut.model_validate(establishment)


@router.post("s")
async def get_all_establishments(
        criteria: EstablishmentCriteria,
) -> Page[EstablishmentAdminOut]:
    find_query = EstablishmentController.filter("menu")
    if criteria.name_contains is not None and criteria.name_contains != "":
        find_query = (
            find_query
            .annotate(name_lower=RawSQL("LOWER(name)"))
            .filter(name_lower__contains=criteria.name_contains.lower())
        )
    if criteria.establishment_type_id is not None:
        find_query = find_query.filter(establishment_type_id=criteria.establishment_type_id)

    total_rows = await find_query.count()

    total_pages = ceil(total_rows / criteria.size)
    offset = (criteria.page - 1) * criteria.size
    if criteria.sort:
        for s in criteria.sort:
            find_query = find_query.order_by(s.order + s.field)

    establishments = await find_query.offset(offset).limit(criteria.size)

    return Page(total=total_rows, page=criteria.page, size=criteria.size, pages=total_pages,
                items=EstablishmentAdminOut.list_validate(establishments))


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
