from typing import Any, Sequence, cast

from sqlalchemy import ColumnElement, Select, distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Computer, VlanDivision


class ComputerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Вспомогательные методы

    def _build_search_condition(self, search: str) -> ColumnElement[bool]:
        """Условие поиска по имени и описанию компьютера"""

        return or_(
            func.inet_ntoa(Computer._ip).ilike(f"%{search}%"),
            Computer.mac.ilike(f"%{search}%"),
            Computer.name.ilike(f"%{search}%"),
            Computer.info.ilike(f"%{search}%"),
        )

    def _build_search_and_filter_conditions(
        self,
        build: str | None = None,
        pc_room: str | None = None,
        division_id: int | None = None,
        os_id: int | None = None,
        user_id: int | None = None,
        is_disabled: bool | None = None,
        search: str | None = None,
    ) -> list[ColumnElement[bool]]:
        """Собрать список условий WHERE из переданных фильтров"""

        conditions = []

        if build is not None:
            conditions.append(Computer.build == build)
        if pc_room is not None:
            conditions.append(Computer.pc_room == pc_room)
        if division_id is not None:
            conditions.append(Computer.division_id == division_id)
        if os_id is not None:
            conditions.append(Computer.os_id == os_id)
        if user_id is not None:
            conditions.append(Computer.user_id == user_id)
        if is_disabled is not None:
            if is_disabled:
                conditions.append(Computer.status_disabled.has())
            else:
                conditions.append(~Computer.status_disabled.has())
        if search is not None:
            conditions.append(self._build_search_condition(search=search))

        return conditions

    def _base_query_with_relations(self) -> Select[tuple[Computer]]:
        """Базовый SELECT с joinedload всех связей"""

        return select(Computer).options(
            joinedload(Computer.division),
            joinedload(Computer.user),
            joinedload(Computer.os_info),
            joinedload(Computer.status_disabled),
        )

    def _apply_vlan_filter(self, query: Select, vlan_id: int | None) -> Select[Any]:
        """Применить фильтр по VLAN через джойн с VlanDivision"""

        if vlan_id is not None:
            query = query.join(
                VlanDivision, VlanDivision.division_id == Computer.division_id
            ).where(VlanDivision.vlan_id == vlan_id)
        return query

    # Получение/подсчет сущности

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None
    ) -> Sequence[Computer]:
        """Получить все компьютеры с пагинацией и поиском"""

        query = select(Computer)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))
        query = query.offset((page - 1) * limit).limit(limit)

        computers = await self.session.scalars(query)
        return computers.all()

    async def count(
        self,
        build: str | None = None,
        pc_room: str | None = None,
        division_id: int | None = None,
        os_id: int | None = None,
        vlan_id: int | None = None,
        user_id: int | None = None,
        is_disabled: bool | None = None,
        search: str | None = None,
    ) -> int:
        """Подсчитать количество компьютеров с теми же фильтрами"""

        conditions = self._build_search_and_filter_conditions(
            build=build,
            pc_room=pc_room,
            division_id=division_id,
            os_id=os_id,
            user_id=user_id,
            is_disabled=is_disabled,
            search=search,
        )
        query = select(func.count()).select_from(Computer)
        query = self._apply_vlan_filter(query=query, vlan_id=vlan_id)

        if conditions:
            query = query.where(*conditions)

        return await self.session.scalar(query) or 0

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        build: str | None = None,
        pc_room: str | None = None,
        division_id: int | None = None,
        os_id: int | None = None,
        vlan_id: int | None = None,
        user_id: int | None = None,
        is_disabled: bool | None = None,
        search: str | None = None,
    ) -> Sequence[Computer]:
        """Получить все компьютеры со связями, фильтрами и поиском"""

        conditions = self._build_search_and_filter_conditions(
            build=build,
            pc_room=pc_room,
            division_id=division_id,
            os_id=os_id,
            user_id=user_id,
            is_disabled=is_disabled,
            search=search,
        )
        query = self._base_query_with_relations()
        query = self._apply_vlan_filter(query=query, vlan_id=vlan_id)

        if conditions:
            query = query.where(*conditions)

        query = query.offset((page - 1) * limit).limit(limit)

        computers = await self.session.scalars(query)
        return computers.all()

    async def get_by_id(self, computer_id: int) -> Computer | None:
        """Получить один компьютер по ID"""

        return await self.session.scalar(
            select(Computer).where(Computer.id == computer_id)
        )

    async def get_by_id_with_relations(self, computer_id: int) -> Computer | None:
        """Получить один компьютер по ID со всеми связями"""

        return await self.session.scalar(
            self._base_query_with_relations().where(Computer.id == computer_id)
        )

    # Получение/подсчет полей сущености

    async def count_buildings(self, search: str | None = None) -> int:
        """Подсчитать количество корпусов с поиском"""

        query = select(func.count(distinct(Computer.build))).where(
            Computer.build.is_not(None)
        )
        if search is not None:
            query = query.where(Computer.build.ilike(f"%{search}%"))

        return await self.session.scalar(query) or 0

    async def get_all_buildings_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все корпусы с поиском"""

        query = select(Computer.build).distinct().where(Computer.build.is_not(None))
        if search is not None:
            query = query.where(Computer.build.ilike(f"%{search}%"))

        query = query.offset((page - 1) * limit).limit(limit)

        buildings = await self.session.scalars(query)
        return cast(Sequence[str], buildings.all())

    async def count_rooms(self, search: str | None = None) -> int:
        """Подсчитать количество комнат с поиском"""

        query = select(func.count(distinct(Computer.pc_room))).where(
            Computer.pc_room.is_not(None)
        )
        if search is not None:
            query = query.where(Computer.pc_room.ilike(f"%{search}%"))

        return await self.session.scalar(query) or 0

    async def get_all_rooms_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все комнаты с поиском"""

        query = select(Computer.pc_room).distinct().where(Computer.pc_room.is_not(None))
        if search is not None:
            query = query.where(Computer.pc_room.ilike(f"%{search}%"))

        query = query.offset((page - 1) * limit).limit(limit)

        rooms = await self.session.scalars(query)
        return cast(Sequence[str], rooms)

    # Изменение

    async def create(self, **kwargs: Any) -> Computer:
        """Добавить новый компьютер в сессию"""

        computer = Computer(**kwargs)
        self.session.add(computer)
        await self.session.flush()
        return cast(Computer, await self.get_by_id(computer.id))

    async def update(self, computer: Computer, **kwargs: Any) -> Computer:
        """Обновить поля компьютера из переданных kwargs"""

        for key, value in kwargs.items():
            setattr(computer, key, value)
        await self.session.flush()
        return cast(Computer, await self.get_by_id(computer.id))

    async def delete(self, computer: Computer) -> None:
        """Удалить компьютер"""

        await self.session.delete(computer)
        await self.session.flush()
