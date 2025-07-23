from .admin import router as admin_router
from .user import router as user_router
from .registration import router as registration_router
from .mentors import router as mentors_router

# Порядок важен - регистрация должна быть первой
routers = [
    registration_router,
    user_router,
    admin_router,
    mentors_router
]

__all__ = ['routers']