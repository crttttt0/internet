from typing import Sequence

from app.core.exceptions import EntityNotFoundException
from app.models import Server
from app.repositories import ServerRepository
from app.schemas.servers import ServerCreate, ServerUpdate

from .division import DivisionService


class ServerService:
    def __init__(
        self,
        server_repository: ServerRepository,
        division_service: DivisionService,
    ) -> None:
        self.server_repository = server_repository
        self.division_service = division_service

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

        await self.division_service.get_by_id(division_id=division_id)

    async def get_all(self, skip: int, limit: int) -> Sequence[Server]:
        """Получить все серверы с пагинацией"""

        return await self.server_repository.get_all(skip=skip, limit=limit)

    async def get_all_with_relations(self, skip: int, limit: int) -> Sequence[Server]:
        """Получить все серверы с пагинацией, подразделениями и VLAN-ами"""

        return await self.server_repository.get_all_with_relations(
            skip=skip, limit=limit
        )

    async def get_by_id(self, server_id: int) -> Server:
        """Получить сервер по ID"""

        return await self._get_or_raise(server_id=server_id)

    async def get_by_id_with_relations(self, server_id: int) -> Server:
        """Получить сервер по ID с подразделением и VLAN-ами"""

        return await self._get_with_relations_or_raise(server_id=server_id)

    async def create(self, server: ServerCreate) -> Server:
        """Создать новый сервер"""

        data = server.model_dump()
        if data.get("division_id") is not None:
            await self._check_division_exists(division_id=data["division_id"])
        return await self.server_repository.create(**data)

    async def update(self, server_id: int, server: ServerUpdate) -> Server:
        """Обновить данные сервера по ID"""

        db_server = await self._get_or_raise(server_id=server_id)
        data = server.model_dump(exclude_none=True)
        if "division_id" in data:
            await self._check_division_exists(division_id=data["division_id"])
        return await self.server_repository.update(db_server, **data)

    async def delete(self, server_id: int) -> None:
        """Удалить сервер по ID"""

        db_server = await self._get_or_raise(server_id=server_id)
        await self.server_repository.delete(server=db_server)
