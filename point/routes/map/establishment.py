import math
from uuid import UUID

from fastapi import APIRouter, Depends, BackgroundTasks

from point.auth import get_user
from point.controllers import EstablishmentController, EstablishmentRatingController, UserVisitController
from point.services import CoordinatesService
from point.view import PointWithScale, EstablishmentPreview, NearEstablishmentCriteria, EstablishmentOut, AuthUser

router = APIRouter()


@router.post("s")
async def get_establishments(location: PointWithScale) -> list[EstablishmentPreview]:
    limit = CoordinatesService.process_scale(scale=math.floor(location.scale))
    if limit == 0:
        return []

    rectangle = CoordinatesService.latlon_bounds_mercator(location)
    establishments = await EstablishmentController.get_establishments_by_rectangle(rectangle, limit)
    return EstablishmentPreview.list_validate(establishments)


@router.post("s/near")
async def get_establishments_near(
        criteria: NearEstablishmentCriteria,
) -> list[EstablishmentPreview]:
    establishments = await EstablishmentController.get_establishments_near(
        lon=criteria.location.longitude,
        lat=criteria.location.latitude,
        limit=25,
        name_contains=criteria.name,
    )
    establishments.sort(key=lambda establishment: establishment.rating, reverse=True)

    return EstablishmentPreview.list_validate(establishments)


@router.get("/{establishment_id}")
async def get_establishment(
        establishment_id: UUID,
        background_tasks: BackgroundTasks,
        user: AuthUser = Depends(get_user),
) -> EstablishmentOut:
    establishment = await EstablishmentController.get("menu", id=establishment_id)
    establishment.user_rating = await EstablishmentRatingController.get_user_rating(
        establishment_id=establishment_id,
        user_id=user.id
    )
    background_tasks.add_task(UserVisitController.add_user_visit, user_id=user.id, establishment_id=establishment_id)

    return EstablishmentOut.model_validate(establishment)
