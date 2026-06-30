from typing import Sequence

from app.core.exceptions import BusinessRuleViolationException, EntityNotFoundException
from app.models import Division
from app.repositories import DivisionRepository
from app.schemas.divisions import DivisionCreate, DivisionUpdate


class DivisionService:
    def __init__(self, division_repository: DivisionRepository) -> None:
        self.division_repository = division_repository

    # Вспомогательные методы

    async def _get_or_raise(self, division_id: int) -> Division:
        """Получить подразделение по ID или выбросить исключение"""

        db_division = await self.division_repository.get_by_id(division_id=division_id)
        if not db_division:
            raise EntityNotFoundException(
                f"Подразделение с ID {division_id} не найдено"
            )
        return db_division

    async def _get_with_relations_or_raise(self, division_id: int) -> Division:
        """Получить подразделение с VLAN-ами по ID или выбросить исключение"""

        db_division = await self.division_repository.get_by_id_with_relations(
            division_id=division_id
        )
        if not db_division:
            raise EntityNotFoundException(
                f"Подразделение с ID {division_id} не найдено"
            )
        return db_division

    # Получение

    async def get_by_id(self, division_id: int) -> Division:
        """Получить подразделение по ID"""

        return await self._get_or_raise(division_id=division_id)

    async def get_by_id_with_relations(self, division_id: int) -> Division:
        """Получить подразделение по ID с VLAN-ами"""

        return await self._get_with_relations_or_raise(division_id=division_id)

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[Division], int]:
        """Получить все подразделения с пагинацией и поиском"""

        items = await self.division_repository.get_all_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.division_repository.count(search=search)
        return items, total

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        stc: str | None = None,
        branch: str | None = None,
        department: str | None = None,
        vlan_id: int | None = None,
        search: str | None = None,
    ) -> tuple[Sequence[Division], int]:
        """Получить все подразделения с пагинацией, связями и фильтрами"""

        items = await self.division_repository.get_all_with_relations_search_filters(
            page=page,
            limit=limit,
            stc=stc,
            branch=branch,
            department=department,
            vlan_id=vlan_id,
            search=search,
        )
        total = await self.division_repository.count(
            stc=stc,
            branch=branch,
            department=department,
            vlan_id=vlan_id,
            search=search,
        )
        return items, total

    # Получение фильтров

    async def get_all_stc_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные НТК с пагинацией и поиском"""

        items = await self.division_repository.get_all_stc_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.division_repository.count_stc(search=search)
        return items, total

    async def get_all_branches_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные отделения с пагинацией и поиском"""

        items = await self.division_repository.get_all_branches_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.division_repository.count_branches(search=search)
        return items, total

    async def get_all_departments_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные отделы с пагинацией и поиском"""

        items = await self.division_repository.get_all_departments_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.division_repository.count_departments(search=search)
        return items, total

    # Изменение

    async def create(self, division: DivisionCreate) -> Division:
        """Создать новое подразделение"""

        return await self.division_repository.create(**division.model_dump())

    async def update(self, division_id: int, division: DivisionUpdate) -> Division:
        """Обновить данные подразделения по ID"""

        db_division = await self._get_or_raise(division_id=division_id)
        return await self.division_repository.update(
            db_division, **division.model_dump(exclude_none=True)
        )

    from app.core.exceptions import (
        BusinessRuleViolationException,
        EntityNotFoundException,
    )

    async def delete(self, division_id: int) -> None:
        """Удалить подразделение по ID"""

        db_division = await self._get_or_raise(division_id=division_id)

        if await self.division_repository.has_users(division_id=division_id):
            raise BusinessRuleViolationException(
                f"Невозможно удалить подразделение с ID {division_id}: есть привязанные пользователи"
            )
        if await self.division_repository.has_computers(division_id=division_id):
            raise BusinessRuleViolationException(
                f"Невозможно удалить подразделение с ID {division_id}: есть привязанные компьютеры"
            )

        await self.division_repository.delete(division=db_division)
