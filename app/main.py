from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AccessDeniedException,
    AuthenticationFailedException,
    BusinessRuleViolationException,
    EntityAlreadyExistsException,
    EntityNotFoundException,
)


def create_app() -> FastAPI:
    """
    Создает приложение, инициализирует exception-handler'ы
    для перевода исключений в HTTP-ошибки
    """

    app = FastAPI(
        title=settings.app.NAME,
        summary=settings.app.SUMMARY,
        version=settings.app.VERSION,
    )

    app.include_router(api_router)

    @app.exception_handler(EntityNotFoundException)
    async def entity_not_found_handler(
        request: Request, exc: EntityNotFoundException
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.detail})

    @app.exception_handler(EntityAlreadyExistsException)
    async def entity_already_exists_handler(
        request: Request, exc: EntityAlreadyExistsException
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.detail})

    @app.exception_handler(AuthenticationFailedException)
    async def authentication_failed_handler(
        request: Request, exc: AuthenticationFailedException
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": exc.detail})

    @app.exception_handler(AccessDeniedException)
    async def access_denied_handler(
        request: Request, exc: AccessDeniedException
    ) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": exc.detail})

    @app.exception_handler(BusinessRuleViolationException)
    async def business_rule_violation_handler(
        request: Request, exc: BusinessRuleViolationException
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.detail})

    @app.get("/health", tags=["health"])
    async def health():
        """Проверка работоспособности сервера"""

        return {"status": "Ок"}

    return app


app = create_app()
