from .computers import router as computers_router
from .divisions import router as divisions_router
from .os import router as os_router
from .status_disabled import router as status_disabled_router
from .users import router as users_router

__all__ = [
    "users_router",
    "divisions_router",
    "os_router",
    "status_disabled_router",
    "computers_router",
]
