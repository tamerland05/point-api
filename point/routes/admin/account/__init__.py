from fastapi import APIRouter

from .purpose import router as purpose_router

router = APIRouter(tags=["Account"])

router.include_router(purpose_router, prefix="/purpose")
