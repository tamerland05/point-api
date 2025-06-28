from uuid import UUID

from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import PurposeIcon


class PurposeIconController(BaseController[PurposeIcon]):
    model = PurposeIcon
    error_code = ErrorCode.PURPOSE_ICON_NOT_FOUND

    @classmethod
    async def get_purpose_icon(cls, purpose_icon_id: UUID) -> model:
        return await cls.get(id=purpose_icon_id, enabled=True)

    @classmethod
    async def get_all_purpose_icons(cls) -> list[model]:
        return await cls.filter(enabled=True)
