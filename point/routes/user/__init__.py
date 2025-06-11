from fastapi import APIRouter

from .auth import router as auth_router
from .employee import router as employee_router

router = APIRouter(tags=["User"])

router.include_router(auth_router, prefix="/auth")
router.include_router(employee_router, prefix="/employee")
