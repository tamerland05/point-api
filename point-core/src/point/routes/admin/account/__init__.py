from fastapi import APIRouter

from .invitation import router as invitation_router
from .purpose import router as purpose_router

router = APIRouter(tags=["Account"])

router.include_router(invitation_router, prefix="/invitation")
router.include_router(purpose_router, prefix="/purpose")
