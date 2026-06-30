from datetime import date
from typing import Any, Sequence, cast

from sqlalchemy import ColumnElement, Select, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Division, Server


class ServerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Вспомогательные методы

    def _build_search_condition(self, search: str) -> ColumnElement[bool]:
        """Условие поиска по IP и MAC-адресу"""

        return or_(
            Server.mac.ilike(f"%{search}%"),
            func.inet_ntoa(Server._ip).ilike(f"%{search}%"),
        )

    def _build_search_and_filter_conditions(
        self,
        room: str | None = None,
        build: str | None = None,
        division_id: int | None = None,
        admin_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> list[ColumnElement[bool]]:
        """Собрать список условий WHERE из переданных фильтров"""

        conditions = []

        if room is not None:
            conditions.append(Server.room == room)
        if build is not None:
            conditions.append(Server.build == build)
        if division_id is not None:
            conditions.append(Server.division_id == division_id)
        if admin_id is not None:
            conditions.append(Server.admin_id == admin_id)
        if date_from is not None:
            conditions.append(Server.date >= date_from)
        if date_to is not None:
            conditions.append(Server.date <= date_to)
        if search is not None:
            conditions.append(self._build_search_condition(search=search))

        return conditions

    def _base_query_with_relations(self) -> Select[tuple[Server]]:
        """Базовый SELECT с загрузкой подразделения и его VLAN-ов"""

        return select(Server).options(
            joinedload(Server.division).selectinload(Division.vlans),
        )

    # Получение/подсчет

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[Server]:
        """Получить все серверы с пагинацией и поиском по IP и MAC"""

        query = select(Server)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))
        query = query.offset((page - 1) * limit).limit(limit)
        return (await self.session.scalars(query)).all()

    async def count(
        self,
        room: str | None = None,
        build: str | None = None,
        division_id: int | None = None,
        admin_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
    ) -> int:
        """Подсчитать количество серверов с фильтрами"""

        conditions = self._build_search_and_filter_conditions(
            room=room,
            build=build,
            division_id=division_id,
            admin_id=admin_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )
        query = select(func.count()).select_from(Server)
        if conditions:
            query = query.where(*conditions)
        return await self.session.scalar(query) or 0

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
    ) -> Sequence[Server]:
        """Получить все серверы с подразделением, VLAN-ами, пагинацией, фильтрами и поиском"""

        conditions = self._build_search_and_filter_conditions(
            room=room,
            build=build,
            division_id=division_id,
            admin_id=admin_id,
            date_from=date_from,
            date_to=date_to,
            search=search,
        )
        query = self._base_query_with_relations()
        if conditions:
            query = query.where(*conditions)
        query = query.offset((page - 1) * limit).limit(limit)
        return (await self.session.scalars(query)).unique().all()

    async def get_by_id(self, server_id: int) -> Server | None:
        """Получить один сервер по ID"""

        return await self.session.scalar(select(Server).where(Server.id == server_id))

    async def get_by_id_with_relations(self, server_id: int) -> Server | None:
        """Получить один сервер по ID с подразделением и VLAN-ами"""

        return await self.session.scalar(
            self._base_query_with_relations().where(Server.id == server_id)
        )

    # Получение/подсчет полей сущности

    async def count_builds(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных корпусов с поиском"""

        query = select(func.count(distinct(Server.build))).where(
            Server.build.is_not(None)
        )
        if search is not None:
            query = query.where(Server.build.ilike(f"%{search}%"))
        return await self.session.scalar(query) or 0

    async def get_all_builds_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные корпусы с поиском"""

        query = select(Server.build).distinct().where(Server.build.is_not(None))
        if search is not None:
            query = query.where(Server.build.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)
        return cast(Sequence[str], (await self.session.scalars(query)).all())

    async def count_rooms(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных комнат с поиском"""

        query = select(func.count(distinct(Server.room))).where(
            Server.room.is_not(None)
        )
        if search is not None:
            query = query.where(Server.room.ilike(f"%{search}%"))
        return await self.session.scalar(query) or 0

    async def get_all_rooms_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные комнаты с поиском"""

        query = select(Server.room).distinct().where(Server.room.is_not(None))
        if search is not None:
            query = query.where(Server.room.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)
        return cast(Sequence[str], (await self.session.scalars(query)).all())

    # Изменение

    async def create(self, **kwargs: Any) -> Server:
        """Добавить новый сервер"""

        server = Server(**kwargs)
        self.session.add(server)
        await self.session.flush()
        return cast(Server, await self.get_by_id(server.id))

    async def update(self, server: Server, **kwargs: Any) -> Server:
        """Обновить поля сервера"""

        for key, value in kwargs.items():
            setattr(server, key, value)
        await self.session.flush()
        return cast(Server, await self.get_by_id(server.id))

    async def delete(self, server: Server) -> None:
        """Удалить сервер"""

        await self.session.delete(server)
        await self.session.flush()
