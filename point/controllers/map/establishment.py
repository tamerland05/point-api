from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Establishment


class EstablishmentController(BaseController[Establishment]):
    model = Establishment
    error_code = ErrorCode.ESTABLISHMENT_NOT_FOUND

    @classmethod
    async def get_establishment(cls, establishment_id: UUID) -> model:
        return await cls.get("menu", id=establishment_id)
