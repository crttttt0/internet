from typing import Any, Sequence, cast

from sqlalchemy import ColumnElement, Select, distinct, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Division, VlanDivision


class DivisionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Вспомогательные методы

    def _build_search_condition(self, search: str) -> ColumnElement[bool]:
        """Условие поиска по НТК, отделению и отделу"""

        return or_(
            Division.stc.ilike(f"%{search}%"),
            Division.branch.ilike(f"%{search}%"),
            Division.department.ilike(f"%{search}%"),
        )

    def _build_search_and_filter_conditions(
        self,
        stc: str | None = None,
        branch: str | None = None,
        department: str | None = None,
        search: str | None = None,
    ) -> list[ColumnElement[bool]]:
        """Собрать список условий WHERE из переданных фильтров"""

        conditions = []

        if stc is not None:
            conditions.append(Division.stc == stc)
        if branch is not None:
            conditions.append(Division.branch == branch)
        if department is not None:
            conditions.append(Division.department == department)
        if search is not None:
            conditions.append(self._build_search_condition(search=search))

        return conditions

    def _base_query_with_relations(self) -> Select[tuple[Division]]:
        """Базовый SELECT с загрузкой VLAN-ов"""

        return select(Division).options(selectinload(Division.vlans))

    def _apply_vlan_filter(self, query: Select, vlan_id: int | None) -> Select[Any]:
        if vlan_id is not None:
            query = query.join(
                VlanDivision, VlanDivision.division_id == Division.id
            ).where(VlanDivision.vlan_id == vlan_id)
        return query

    # Получение/подсчет

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[Division]:
        """Получить все подразделения с пагинацией и поиском"""

        query = select(Division)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))
        query = query.offset((page - 1) * limit).limit(limit)

        divisions = await self.session.scalars(query)
        return divisions.all()

    async def count(
        self,
        stc: str | None = None,
        branch: str | None = None,
        department: str | None = None,
        vlan_id: int | None = None,
        search: str | None = None,
    ) -> int:
        """Подсчитать количество подразделений с фильтрами"""

        conditions = self._build_search_and_filter_conditions(
            stc=stc, branch=branch, department=department, search=search
        )
        query = select(func.count()).select_from(Division)
        query = self._apply_vlan_filter(query=query, vlan_id=vlan_id)

        if conditions:
            query = query.where(*conditions)

        return await self.session.scalar(query) or 0

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        stc: str | None = None,
        branch: str | None = None,
        department: str | None = None,
        vlan_id: int | None = None,
        search: str | None = None,
    ) -> Sequence[Division]:
        """Получить все подразделения со связями, фильтрами и поиском"""

        conditions = self._build_search_and_filter_conditions(
            stc=stc, branch=branch, department=department, search=search
        )
        query = self._base_query_with_relations()
        query = self._apply_vlan_filter(query=query, vlan_id=vlan_id)

        if conditions:
            query = query.where(*conditions)
        query = query.offset((page - 1) * limit).limit(limit)

        divisions = await self.session.scalars(query)
        return divisions.all()

    async def get_by_id(self, division_id: int) -> Division | None:
        """Получить одно подразделение по ID"""

        return await self.session.scalar(
            select(Division).where(Division.id == division_id)
        )

    async def get_by_id_with_relations(self, division_id: int) -> Division | None:
        """Получить одно подразделение по ID с VLAN-ами"""

        return await self.session.scalar(
            self._base_query_with_relations().where(Division.id == division_id)
        )

    # Получение/подсчет полей сущности

    async def count_stc(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных НТК с поиском"""

        query = select(func.count(distinct(Division.stc))).where(
            Division.stc.is_not(None)
        )
        if search is not None:
            query = query.where(Division.stc.ilike(f"%{search}%"))
        return await self.session.scalar(query) or 0

    async def get_all_stc_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные НТК с поиском"""

        query = select(Division.stc).distinct().where(Division.stc.is_not(None))
        if search is not None:
            query = query.where(Division.stc.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)
        return cast(Sequence[str], (await self.session.scalars(query)).all())

    async def count_branches(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных отделений с поиском"""

        query = select(func.count(distinct(Division.branch))).where(
            Division.branch.is_not(None)
        )
        if search is not None:
            query = query.where(Division.branch.ilike(f"%{search}%"))
        return await self.session.scalar(query) or 0

    async def get_all_branches_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные отделения с поиском"""

        query = select(Division.branch).distinct().where(Division.branch.is_not(None))
        if search is not None:
            query = query.where(Division.branch.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)
        return cast(Sequence[str], (await self.session.scalars(query)).all())

    async def count_departments(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных отделов с поиском"""

        query = select(func.count(distinct(Division.department))).where(
            Division.department.is_not(None)
        )
        if search is not None:
            query = query.where(Division.department.ilike(f"%{search}%"))
        return await self.session.scalar(query) or 0

    async def get_all_departments_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные отделы с поиском"""

        query = (
            select(Division.department)
            .distinct()
            .where(Division.department.is_not(None))
        )
        if search is not None:
            query = query.where(Division.department.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)
        return cast(Sequence[str], (await self.session.scalars(query)).all())

    # Проверка связей

    async def has_users(self, division_id: int) -> bool:
        """Проверить, есть ли пользователи привязанные к подразделению"""

        from app.models import User

        result = await self.session.scalar(
            select(exists().where(User.division_id == division_id))
        )
        return bool(result)

    async def has_computers(self, division_id: int) -> bool:
        """Проверить, есть ли компьютеры привязанные к подразделению"""

        from app.models import Computer

        result = await self.session.scalar(
            select(exists().where(Computer.division_id == division_id))
        )
        return bool(result)

    # Изменение

    async def create(self, **kwargs: Any) -> Division:
        """Добавить новое подразделение"""

        division = Division(**kwargs)
        self.session.add(division)
        await self.session.flush()

        return cast(Division, await self.get_by_id(division.id))

    async def update(self, division: Division, **kwargs: Any) -> Division:
        """Обновить поля подразделения"""

        for key, value in kwargs.items():
            setattr(division, key, value)
        await self.session.flush()

        return cast(Division, await self.get_by_id(division.id))

    async def delete(self, division: Division) -> None:
        """Удалить подразделение"""

        await self.session.delete(division)
        await self.session.flush()
