from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends

from point.auth import get_user
from point.controllers import AssetController
from point.view import AuthUser, AssetOut, fake, random_address

router = APIRouter(tags=["Asset"])


@router.get("s")
async def get_assets() -> list[AssetOut]:
    assets = await AssetController.get_all_assets()
    return [AssetOut.model_validate(a) for a in assets]
