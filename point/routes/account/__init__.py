from fastapi import APIRouter

from .auth import router as auth_router
from .employee import router as employee_router
from .purpose import router as purpose_router
from .user import router as user_router

router = APIRouter(tags=["Account"])

router.include_router(auth_router, prefix="/auth")
router.include_router(employee_router, prefix="/employee")
router.include_router(purpose_router, prefix="/purpose")
router.include_router(user_router, prefix="/user")
