from fastapi import APIRouter

from .webhook import router as webhook_router
from point.config import settings

router = APIRouter()

router.include_router(webhook_router, prefix="/" + settings.main_bot_token + "/webhook", include_in_schema=False)
