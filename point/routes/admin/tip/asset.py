from uuid import UUID

from fastapi import APIRouter

from point.controllers import AssetController
from point.view import AssetCreateIn, AssetUpdateIn, AssetAdminOut

router = APIRouter()


@router.get("/{asset_id}")
async def get_asset(
        asset_id: UUID,
) -> AssetAdminOut:
    asset = await AssetController.get(id=asset_id)
    return AssetAdminOut.model_validate(asset)


@router.get("s")
async def get_all_assets() -> list[AssetAdminOut]:
    assets = await AssetController.filter()
    return [AssetAdminOut.model_validate(a) for a in assets]


@router.post("")
async def create_asset(
        asset_in: AssetCreateIn,
) -> AssetAdminOut:
    asset = await AssetController.create(asset_in)
    return AssetAdminOut.model_validate(asset)


@router.put("/{asset_id}")
async def update_asset(
        asset_id: UUID,
        asset_update_in: AssetUpdateIn,
) -> AssetAdminOut:
    asset = await AssetController.update(
        model_update_in=asset_update_in,
        id=asset_id
    )
    return AssetAdminOut.model_validate(asset)


@router.delete("/{asset_id}")
async def delete_asset(
        asset_id: UUID,
) -> None:
    await AssetController.delete_by_uuid(model_id=asset_id)
