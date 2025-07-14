from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentController
from point.view import PointWithScale, EstablishmentPreview, NearEstablishmentCriteria, EstablishmentOut

router = APIRouter()


@router.post("s")
async def get_establishments(location: PointWithScale) -> list[EstablishmentPreview]:
    establishments = await EstablishmentController.filter("menu", enabled=True)
    establishments = EstablishmentPreview.list_validate(establishments)

    establishments.sort(key=lambda establishment: location.distance(establishment.position))

    return establishments


@router.post("s/near")
async def get_establishments_near(
        criteria: NearEstablishmentCriteria,
) -> list[EstablishmentPreview]:
    establishments = await EstablishmentController.filter("menu", enabled=True)
    establishments = [
        EstablishmentPreview.model_validate(e) for e in establishments
        if e.name is None or criteria.name in e.name
    ]

    establishments.sort(key=lambda establishment: criteria.location.distance(establishment.position))

    return establishments


@router.get("/{establishment_id}")
async def get_establishment(establishment_id: UUID) -> EstablishmentOut:
    establishment = await EstablishmentController.get("menu", id=establishment_id)
    return EstablishmentOut.model_validate(establishment)
