from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Establishment
from point.services.wallet import ServiceWalletController
from point.view import EstablishmentDbCreateIn


class EstablishmentController(BaseController[Establishment]):
    model = Establishment
    error_code = ErrorCode.ESTABLISHMENT_NOT_FOUND

    @classmethod
    async def get_establishment(cls, establishment_id: UUID) -> model:
        return await cls.get("menu", id=establishment_id)

    @classmethod
    async def admin_create(cls, establishment_create_in: EstablishmentDbCreateIn) -> Establishment:
        address, seed = await ServiceWalletController.create()

        establishment = await cls.model.create(
            **establishment_create_in.model_dump(mode="json"),
            service_wallet=address,
            service_wallet_seed=seed,
        )
        await establishment.fetch_related("menu")

        return establishment
