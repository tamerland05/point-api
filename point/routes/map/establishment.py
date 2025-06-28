from uuid import UUID

from fastapi import APIRouter
from fastapi.params import Depends

from point.auth import get_user
from point.controllers import EstablishmentController
from point.view import AuthUser, PointWithScale, EstablishmentPreview, NearEstablishmentCriteria, EstablishmentOut
from point.view.utils import point_distance

router = APIRouter()


@router.post("s")
async def get_establishments(location: PointWithScale) -> list[EstablishmentPreview]:
    establishments = await EstablishmentController.filter("menu", enabled=True)
    establishments = [EstablishmentPreview.model_validate(e) for e in establishments]

    establishments.sort(key=lambda establishment: point_distance(location, establishment.position))

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

    establishments.sort(key=lambda establishment: point_distance(criteria.location, establishment.position))

    return establishments


@router.get("/{establishment_id}")
async def get_establishment(establishment_id: UUID) -> EstablishmentOut:
    establishment = await EstablishmentController.get("menu", id=establishment_id)
    return EstablishmentOut.model_validate(establishment)


@router.post("/{establishment_id}/rate")
async def set_establishment_rate(establishment_id: UUID, mark: int, user: AuthUser = Depends(get_user)) -> None:
    return None
