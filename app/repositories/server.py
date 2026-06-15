from typing import Any, Sequence, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Server


class ServerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_query_with_relations(self):
        """Базовый SELECT с загрузкой подразделения и его VLAN-ов"""

        return select(Server).options(
            joinedload(Server.division).selectinload("vlans"),
        )

    async def get_all(self, skip: int, limit: int) -> Sequence[Server]:
        """Получить все серверы с пагинацией"""

        servers = await self.session.scalars(select(Server).offset(skip).limit(limit))
        return servers.all()

    async def get_all_with_relations(self, skip: int, limit: int) -> Sequence[Server]:
        """Получить все серверы с пагинацией вместе с подразделением и VLAN-ами"""

        servers = await self.session.scalars(
            self._base_query_with_relations().offset(skip).limit(limit)
        )
        return servers.unique().all()

    async def get_by_id(self, server_id: int) -> Server | None:
        """Получить один сервер по ID"""

        return await self.session.scalar(select(Server).where(Server.id == server_id))

    async def get_by_id_with_relations(self, server_id: int) -> Server | None:
        """Получить один сервер по ID с развёрнутым подразделением и VLAN-ами"""

        return await self.session.scalar(
            self._base_query_with_relations().where(Server.id == server_id)
        )

    async def create(self, **kwargs: Any) -> Server:
        """Добавить новый сервер в сессию"""

        server = Server(**kwargs)
        self.session.add(server)
        await self.session.flush()
        return cast(Server, await self.get_by_id(server.id))

    async def update(self, server: Server, **kwargs: Any) -> Server:
        """Обновить поля сервера из переданных kwargs"""

        for key, value in kwargs.items():
            setattr(server, key, value)
        await self.session.flush()
        return cast(Server, await self.get_by_id(server.id))

    async def delete(self, server: Server) -> None:
        """Удалить сервер"""

        await self.session.delete(server)
        await self.session.flush()
