from .auth_routes import router as auth_router
from .core_routes import router as core_router
from .stubs import router as stubs_router

__all__ = [
    "auth_router",
    "core_router",
    "stubs_router",
]


