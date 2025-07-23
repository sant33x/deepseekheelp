from .admin import router as admin_router
from .user import router as user_router
from .registration import router as registration_router
from .mentors import router as mentors_router

routers = [
    registration_router,
    user_router,
    admin_router,
    mentors_router
]