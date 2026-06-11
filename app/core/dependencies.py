from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.repositories import (
    ComputerRepository,
    DivisionRepository,
    OSRepository,
    StatusDisabledRepository,
    UserRepository,
)
from app.services import (
    ComputerService,
    DivisionService,
    OSService,
    StatusDisabledService,
    UserService,
)

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


def get_os_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> OSRepository:
    """Предоставить репозиторий операционных систем с текущей сессией БД"""

    return OSRepository(session)


def get_status_disabled_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> StatusDisabledRepository:
    """Предоставить репозиторий статусов отключения с текущей сессией БД"""
    return StatusDisabledRepository(session)


def get_computer_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ComputerRepository:
    """Предоставить репозиторий компьютеров с текущей сессией БД"""
    return ComputerRepository(session)


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


def get_os_service(
    os_repository: Annotated[OSRepository, Depends(get_os_repository)],
) -> OSService:
    """Предоставить сервис операционных систем с внедрённым репозиторием"""

    return OSService(os_repository)


def get_status_disabled_service(
    status_disabled_repository: Annotated[
        StatusDisabledRepository, Depends(get_status_disabled_repository)
    ],
) -> StatusDisabledService:
    """Предоставить сервис статусов отключения с внедрённым репозиторием"""
    return StatusDisabledService(status_disabled_repository)


def get_computer_service(
    computer_repository: Annotated[
        ComputerRepository, Depends(get_computer_repository)
    ],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> ComputerService:
    """Предоставить сервис компьютеров с внедрёнными репозиторием и сервисом подразделений"""
    return ComputerService(computer_repository, division_service)
