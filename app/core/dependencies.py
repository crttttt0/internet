from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.repositories import DivisionRepository, UserRepository
from app.services import DivisionService, UserService

# Репозитории


def get_division_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DivisionRepository:
    """Предоставить репозиторий подразделений с текущей сессией БД"""

    return DivisionRepository(session)


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    """Предоставить репозиторий пользователей с текущей сессией БД"""

    return UserRepository(session)


# Сервисы


def get_division_service(
    division_repository: Annotated[
        DivisionRepository, Depends(get_division_repository)
    ],
) -> DivisionService:
    """Предоставить сервис подразделений с внедрённым репозиторием"""

    return DivisionService(division_repository)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> UserService:
    """Предоставить сервис пользователей с внедрёнными репозиторием и сервисом подразделений"""

    return UserService(user_repository, division_service)
