from fastapi import APIRouter, Depends

from point.auth import get_user

from .asset import router as asset_router
from .receiver import router as receiver_router
from .send import router as send_router

router = APIRouter(tags=["Tip"], dependencies=[Depends(get_user)])

router.include_router(asset_router, prefix="/asset")
router.include_router(receiver_router, prefix="/receiver")
router.include_router(send_router, prefix="/send")
