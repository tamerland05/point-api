from fastapi import APIRouter, Depends

from point.auth import get_user

from .establishment import router as establishment_router
from .establishment_type import router as establishment_type_router
from .menu_item import router as menu_item_router

router = APIRouter(dependencies=[Depends(get_user)], tags=["Map"])

router.include_router(establishment_router, prefix="/establishment")
router.include_router(establishment_type_router, prefix="/establishment-type")
router.include_router(menu_item_router, prefix="/menu-item")
