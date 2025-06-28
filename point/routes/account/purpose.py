from fastapi import APIRouter, Depends

from point.auth import get_user
from point.controllers import PurposeIconController
from point.view import AuthUser, PurposeIconOut

router = APIRouter()


@router.get("-icons")
async def get_purpose_icons(_: AuthUser = Depends(get_user)) -> list[PurposeIconOut]:
    purposes_images = await PurposeIconController.get_all_purpose_icons()
    return [PurposeIconOut.model_validate(e) for e in purposes_images]
