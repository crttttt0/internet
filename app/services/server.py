from datetime import date
from typing import Sequence

from app.core.exceptions import EntityNotFoundException, InvalidForeignKeyException
from app.models import Server
from app.repositories import ServerRepository
from app.schemas.servers import ServerCreate, ServerUpdate

from .division import DivisionService
from .user import UserService


class ServerService:
    def __init__(
        self,
        server_repository: ServerRepository,
        division_service: DivisionService,
        user_service: UserService,
    ) -> None:
        self.server_repository = server_repository
        self.division_service = division_service
        self.user_service = user_service

    # Вспомогательные методы

    async def _get_or_raise(self, server_id: int) -> Server:
        """Получить сервер по ID или выбросить исключение"""

        db_server = await self.server_repository.get_by_id(server_id=server_id)
        if not db_server:
            raise EntityNotFoundException(f"Сервер с ID {server_id} не найден")
        return db_server

    async def _get_with_relations_or_raise(self, server_id: int) -> Server:
        """Получить сервер со связями по ID или выбросить исключение"""

        db_server = await self.server_repository.get_by_id_with_relations(
            server_id=server_id
        )
        if not db_server:
            raise EntityNotFoundException(f"Сервер с ID {server_id} не найден")
        return db_server

    async def _check_division_exists(self, division_id: int) -> None:
        """Проверить, существует ли подразделение, если нет — выбросить исключение"""

        try:
            await self.division_service.get_by_id(division_id=division_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(
                f"Подразделение с ID {division_id} не найдено"
            )

    async def _check_user_exists(self, user_id: int) -> None:
        """Проверить, существует ли пользователь, если нет — выбросить исключение"""

        try:
            await self.user_service.get_by_id(user_id=user_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(f"Пользователь с ID {user_id} не найден")

    # Получение

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[Server], int]:
        """Получить все серверы с пагинацией и поиском по IP и MAC"""

        items = await self.server_repository.get_all_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.server_repository.count(search=search)
        return items, total

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        room: str | None = None,
        build: str | None = None,
        division_id: int | None = None,
        admin_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> tuple[Sequence[Server], int]:
        """Получить все серверы с подразделением, VLAN-ами, пагинацией, фильтрами и поиском"""

        items = await self.server_repository.get_all_with_relations_search_filters(
            page=page,
            limit=limit,
            room=room,
            build=build,
            division_id=division_id,
            admin_id=admin_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )
        total = await self.server_repository.count(
            room=room,
            build=build,
            division_id=division_id,
            admin_id=admin_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )
        return items, total

    async def get_by_id(self, server_id: int) -> Server:
        """Получить сервер по ID"""

        return await self._get_or_raise(server_id=server_id)

    async def get_by_id_with_relations(self, server_id: int) -> Server:
        """Получить сервер по ID с подразделением и VLAN-ами"""

        return await self._get_with_relations_or_raise(server_id=server_id)

    # Получение полей сущности

    async def get_all_builds_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные корпусы с пагинацией и поиском"""

        items = await self.server_repository.get_all_builds_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.server_repository.count_builds(search=search)
        return items, total

    async def get_all_rooms_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные комнаты с пагинацией и поиском"""

        items = await self.server_repository.get_all_rooms_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.server_repository.count_rooms(search=search)
        return items, total

    # Изменение

    async def create(self, server: ServerCreate) -> Server:
        """Создать новый сервер"""

        data = server.model_dump()

        if data.get("division_id") is not None:
            await self._check_division_exists(division_id=data["division_id"])
        if data.get("admin_id") is not None:
            await self._check_user_exists(user_id=data["admin_id"])

        return await self.server_repository.create(**data)

    async def update(self, server_id: int, server: ServerUpdate) -> Server:
        """Обновить данные сервера по ID"""

        db_server = await self._get_or_raise(server_id=server_id)
        data = server.model_dump(exclude_none=True)

        if "division_id" in data:
            await self._check_division_exists(division_id=data["division_id"])
        if "admin_id" in data:
            await self._check_user_exists(user_id=data["admin_id"])

        return await self.server_repository.update(db_server, **data)

    async def delete(self, server_id: int) -> None:
        """Удалить сервер по ID"""

        db_server = await self._get_or_raise(server_id=server_id)
        await self.server_repository.delete(server=db_server)
