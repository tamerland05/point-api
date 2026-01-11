from fastapi import APIRouter

from .asset import router as asset_router

router = APIRouter(tags=["Tip"])

router.include_router(asset_router, prefix="/asset")
