from uuid import UUID

from fastapi import APIRouter

from point.controllers import PurposeIconController
from point.view import PurposeIconCreateIn, PurposeIconUpdateIn, PurposeIconAdminOut

router = APIRouter()


@router.get("-icon/{purpose_icon_id}")
async def get_purpose_icon(
        purpose_icon_id: UUID,
) -> PurposeIconAdminOut:
    purpose_icon = await PurposeIconController.get(id=purpose_icon_id)
    return PurposeIconAdminOut.model_validate(purpose_icon)


@router.get("-icons")
async def get_all_purpose_icons() -> list[PurposeIconAdminOut]:
    purpose_icons = await PurposeIconController.filter()
    return [PurposeIconAdminOut.model_validate(p) for p in purpose_icons]


@router.post("-icon")
async def create_purpose_icon(
        purpose_icon_in: PurposeIconCreateIn,
) -> PurposeIconAdminOut:
    purpose_icon = await PurposeIconController.create(purpose_icon_in)
    return PurposeIconAdminOut.model_validate(purpose_icon)


@router.put("-icon/{purpose_icon_id}")
async def update_purpose_icon(
        purpose_icon_id: UUID,
        purpose_icon_update_in: PurposeIconUpdateIn,
) -> PurposeIconAdminOut:
    purpose_icon = await PurposeIconController.update(
        model_update_in=purpose_icon_update_in,
        id=purpose_icon_id
    )
    return PurposeIconAdminOut.model_validate(purpose_icon)


@router.delete("-icon/{purpose_icon_id}")
async def delete_purpose_icon(
        purpose_icon_id: UUID,
) -> None:
    await PurposeIconController.delete(id=purpose_icon_id)
