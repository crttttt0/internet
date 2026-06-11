from typing import Any, Sequence, cast

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Computer, Vlan, VlanDivision


class ComputerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _build_filter_conditions(
        self,
        build: str | None = None,
        pc_room: str | None = None,
        division_id: int | None = None,
        os_id: int | None = None,
        user_id: int | None = None,
        is_disabled: bool | None = None,
        search: str | None = None,
    ) -> list:
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
                # Компьютер отключён — запись в status_disabled существует
                conditions.append(Computer.status_disabled.has())
            else:
                conditions.append(~Computer.status_disabled.has())
        if search is not None:
            conditions.append(Computer.name.ilike(f"%{search}%"))

        return conditions

    def _base_query_with_relations(self):
        """Базовый SELECT с joinedload всех связей"""

        return select(Computer).options(
            joinedload(Computer.division),
            joinedload(Computer.user),
            joinedload(Computer.os_info),
            joinedload(Computer.status_disabled),
        )

    async def get_all(self, skip: int, limit: int) -> Sequence[Computer]:
        """Получить все компьютеры с пагинацией"""

        computers = await self.session.scalars(
            select(Computer).offset(skip).limit(limit)
        )
        return computers.all()

    async def get_all_with_relations_search_filters(
        self,
        skip: int,
        limit: int,
        build: str | None = None,
        pc_room: str | None = None,
        division_id: int | None = None,
        os_id: int | None = None,
        vlan_name: str | None = None,
        user_id: int | None = None,
        is_disabled: bool | None = None,
        search: str | None = None,
    ) -> Sequence[Computer]:
        """Получить все компьютеры со связями, фильтрами и поиском"""

        conditions = self._build_filter_conditions(
            build=build,
            pc_room=pc_room,
            division_id=division_id,
            os_id=os_id,
            user_id=user_id,
            is_disabled=is_disabled,
            search=search,
        )
        query = self._base_query_with_relations()

        if vlan_name is not None:
            # JOIN через association table: computers → divisions → vlandiv → vlans
            query = (
                query.join(Computer.division)
                .join(
                    VlanDivision,
                    VlanDivision.division_id == Computer.division_id,
                )
                .join(
                    Vlan,
                    Vlan.id == VlanDivision.vlan_id,
                )
                .where(Vlan.name == vlan_name)
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.offset(skip).limit(limit)

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
