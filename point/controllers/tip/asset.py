from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Asset


class AssetController(BaseController[Asset]):
    error_code: ErrorCode = ErrorCode.ASSET_NOT_FOUND
    model = Asset

    @classmethod
    async def get_asset(cls, asset_id: UUID) -> model:
        return await cls.get(id=asset_id, enabled=True)

    @classmethod
    async def get_all_assets(cls) -> list[model]:
        return await cls.filter(enabled=True)

    # todo: asset price updating
