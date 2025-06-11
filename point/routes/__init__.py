from fastapi import APIRouter

from .admin import router as admin_router
from .earn import router as earn_router
from .map import router as map_router
from .selection import router as selection_router
from .tip import router as tip_router
from .user import router as user_router
from ..config import settings, AppEnv

router = APIRouter()

router.include_router(admin_router, prefix="/admin", include_in_schema=settings.app_env == AppEnv.DEV)
router.include_router(earn_router, prefix="/earn")
router.include_router(map_router, prefix="/map")
router.include_router(selection_router, prefix="/selection")
router.include_router(tip_router, prefix="/tip")
router.include_router(user_router, prefix="/user")
