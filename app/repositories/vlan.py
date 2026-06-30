from typing import Any, Sequence, cast

from sqlalchemy import ColumnElement, Select, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Vlan, VlanDivision


class VlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Вспомогательные методы

    def _build_search_condition(self, search: str) -> ColumnElement[bool]:
        """Условие поиска по названию и ACL VLAN-а"""

        return Vlan.name.ilike(f"%{search}%")

    def _build_search_and_filter_conditions(
        self,
        acl: str | None = None,
        search: str | None = None,
    ) -> list[ColumnElement[bool]]:
        """Собрать список условий WHERE из переданных фильтров"""

        conditions = []
        if acl is not None:
            conditions.append(Vlan.acl == acl)
        if search is not None:
            conditions.append(self._build_search_condition(search=search))
        return conditions

    def _base_query_with_relations(self) -> Select[tuple[Vlan]]:
        """Базовый SELECT с загрузкой подразделений"""

        return select(Vlan).options(selectinload(Vlan.divisions))

    def _apply_division_filter(
        self, query: Select, division_id: int | None
    ) -> Select[Any]:
        """Применить фильтр по подразделению через джойн с VlanDivision"""

        if division_id is not None:
            query = query.join(VlanDivision, VlanDivision.vlan_id == Vlan.id).where(
                VlanDivision.division_id == division_id
            )
        return query

    # Получение/подсчет

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[Vlan]:
        """Получить все VLAN-ы с пагинацией и поиском"""

        query = select(Vlan)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))
        query = query.offset((page - 1) * limit).limit(limit)

        return (await self.session.scalars(query)).all()

    async def count(
        self,
        acl: str | None = None,
        division_id: int | None = None,
        search: str | None = None,
    ) -> int:
        """Подсчитать количество VLAN-ов с фильтрами"""

        conditions = self._build_search_and_filter_conditions(acl=acl, search=search)
        query = select(func.count()).select_from(Vlan)

        query = self._apply_division_filter(query=query, division_id=division_id)
        if conditions:
            query = query.where(*conditions)

        return await self.session.scalar(query) or 0

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        acl: str | None = None,
        division_id: int | None = None,
        search: str | None = None,
    ) -> Sequence[Vlan]:
        """Получить все VLAN-ы с подразделениями, пагинацией, фильтрами и поиском"""

        conditions = self._build_search_and_filter_conditions(acl=acl, search=search)

        query = self._base_query_with_relations()
        query = self._apply_division_filter(query=query, division_id=division_id)
        if conditions:
            query = query.where(*conditions)
        query = query.offset((page - 1) * limit).limit(limit)

        return (await self.session.scalars(query)).all()

    async def get_by_id(self, vlan_id: int) -> Vlan | None:
        """Получить один VLAN по ID"""

        return await self.session.scalar(select(Vlan).where(Vlan.id == vlan_id))

    async def get_by_id_with_relations(self, vlan_id: int) -> Vlan | None:
        """Получить один VLAN по ID с подразделениями"""

        return await self.session.scalar(
            self._base_query_with_relations().where(Vlan.id == vlan_id)
        )

    # Получение/подсчет полей сущности

    async def count_acl(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных ACL с поиском"""

        query = select(func.count(distinct(Vlan.acl))).where(Vlan.acl.is_not(None))
        if search is not None:
            query = query.where(Vlan.acl.ilike(f"%{search}%"))

        return await self.session.scalar(query) or 0

    async def get_all_acl_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные ACL с поиском"""

        query = select(Vlan.acl).distinct().where(Vlan.acl.is_not(None))
        if search is not None:
            query = query.where(Vlan.acl.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)

        acls = await self.session.scalars(query)
        return cast(Sequence[str], acls.all())

    # Изменение

    async def create(self, **kwargs: Any) -> Vlan:
        """Добавить новый VLAN"""

        vlan = Vlan(**kwargs)
        self.session.add(vlan)
        await self.session.flush()
        return cast(Vlan, await self.get_by_id(vlan.id))

    async def update(self, vlan: Vlan, **kwargs: Any) -> Vlan:
        """Обновить поля VLAN-а"""

        for key, value in kwargs.items():
            setattr(vlan, key, value)
        await self.session.flush()
        return cast(Vlan, await self.get_by_id(vlan.id))

    async def delete(self, vlan: Vlan) -> None:
        """Удалить VLAN"""

        await self.session.delete(vlan)
        await self.session.flush()
