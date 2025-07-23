# bot/__init__.py
from .handlers.admin import router as admin_router
from .handlers.user import router as user_router
from .handlers.registration import router as registration_router
from .handlers.mentors import router as mentors_router

__all__ = ['admin_router', 'user_router', 'registration_router', 'mentors_router']