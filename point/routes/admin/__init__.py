from fastapi import APIRouter, Depends

from point.auth.admin import api_admin_key_auth

from .account import router as account_router
from .earn import router as earn_router
from .map import router as establishment_router
from .tip import router as tip_router
from .common import router as common_router

router = APIRouter(dependencies=[Depends(api_admin_key_auth)])

router.include_router(account_router, prefix="/account")
router.include_router(earn_router, prefix="/earn")
router.include_router(common_router, prefix="/common")
router.include_router(establishment_router, prefix="/map")
router.include_router(tip_router, prefix="/tip")
