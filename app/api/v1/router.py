from fastapi import APIRouter

from app.api.v1.endpoints import (
    computers_router,
    divisions_router,
    os_router,
    status_disabled_router,
    users_router,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(divisions_router)
api_router.include_router(users_router)
api_router.include_router(os_router)
api_router.include_router(status_disabled_router)
api_router.include_router(computers_router)
