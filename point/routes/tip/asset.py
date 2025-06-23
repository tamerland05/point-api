from fastapi import APIRouter

from point.controllers import AssetController
from point.view import AssetOut

router = APIRouter()


@router.get("s")
async def get_assets() -> list[AssetOut]:
    assets = await AssetController.get_all_assets()
    return [AssetOut.model_validate(a) for a in assets]
