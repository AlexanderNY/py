from .auth_routes import router as auth_router
from .core_routes import router as core_router
from .wp_routes import router as wp_router
from .tg_routes import router as tg_router
from .tw_routes import router as tw_router
from .vk_routes import router as vk_router
from .curl_routes import router as curl_router
from .cpost_routes import router as cpost_router
from .stubs import router as stubs_router
from .test_routes import router as test_router

__all__ = [
    "auth_router",
    "core_router",
    "wp_router",
    "tg_router",
    "tw_router",
    "vk_router",
    "curl_router",
    "cpost_router",
    "stubs_router",
    "test_router",
]


