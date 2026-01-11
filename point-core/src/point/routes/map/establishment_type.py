from uuid import UUID

from fastapi import APIRouter

from point.controllers import EstablishmentTypeController
from point.view import EstablishmentTypeOut

router = APIRouter()


@router.get("s")
async def get_establishment_types() -> dict[UUID, EstablishmentTypeOut]:
    establishment_types = await EstablishmentTypeController.filter(enabled=True)
    return {e.id: EstablishmentTypeOut.model_validate(e) for e in establishment_types}
