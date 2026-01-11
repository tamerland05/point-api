from fastapi import APIRouter, Depends

from .selection import router as selection_router
from point.auth import get_user

router = APIRouter(dependencies=[Depends(get_user)])

router.include_router(selection_router)
