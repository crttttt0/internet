from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.repositories import (
    ComputerRepository,
    DivisionRepository,
    OSRepository,
    ServerRepository,
    StatusDisabledRepository,
    UserRepository,
    VlanRepository,
)
from app.services import (
    ComputerService,
    DivisionService,
    OSService,
    ServerService,
    StatusDisabledService,
    UserService,
    VlanService,
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


def get_vlan_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> VlanRepository:
    """Предоставить репозиторий VLAN-ов с текущей сессией БД"""

    return VlanRepository(session)


# Сервисы


def get_division_service(
    division_repository: Annotated[
        DivisionRepository, Depends(get_division_repository)
    ],
) -> DivisionService:
    """Предоставить сервис подразделений с внедрённым репозиторием"""

    return DivisionService(division_repository=division_repository)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> UserService:
    """Предоставить сервис пользователей с внедрёнными репозиторием и сервисом подразделений"""

    return UserService(
        user_repository=user_repository, division_service=division_service
    )


def get_os_service(
    os_repository: Annotated[OSRepository, Depends(get_os_repository)],
) -> OSService:
    """Предоставить сервис операционных систем с внедрённым репозиторием"""

    return OSService(os_repository=os_repository)


def get_computer_service(
    computer_repository: Annotated[
        ComputerRepository, Depends(get_computer_repository)
    ],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> ComputerService:
    """Предоставить сервис компьютеров с внедрёнными репозиторием и сервисами подразделений, пользователей и ОС"""

    return ComputerService(
        computer_repository=computer_repository,
        division_service=division_service,
        user_service=user_service,
        os_service=os_service,
    )


def get_status_disabled_service(
    status_disabled_repository: Annotated[
        StatusDisabledRepository, Depends(get_status_disabled_repository)
    ],
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> StatusDisabledService:
    """Предоставить сервис статусов отключения с внедрёнными репозиторием и сервисом компьютеров"""

    return StatusDisabledService(
        status_disabled_repository=status_disabled_repository,
        computer_service=computer_service,
    )


def get_vlan_service(
    vlan_repository: Annotated[VlanRepository, Depends(get_vlan_repository)],
) -> VlanService:
    """Предоставить сервис VLAN-ов с внедрённым репозиторием"""

    return VlanService(vlan_repository=vlan_repository)


def get_server_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ServerRepository:
    """Предоставить репозиторий серверов с текущей сессией БД"""

    return ServerRepository(session)


def get_server_service(
    server_repository: Annotated[ServerRepository, Depends(get_server_repository)],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> ServerService:
    """Предоставить сервис серверов с внедрёнными репозиторием и сервисами подразделений и пользователей"""

    return ServerService(
        server_repository=server_repository,
        division_service=division_service,
        user_service=user_service,
    )
