from typing import Any, Sequence

from sqlalchemy import ColumnElement, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OS


class OSRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Вспомогательные методы

    def _build_search_condition(self, search: str) -> ColumnElement[bool]:
        """Условие поиска по названию ОС"""

        return OS.name.ilike(f"%{search}%")

    # Получение/подсчет

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[OS]:
        """Получить все ОС с пагинацией и поиском"""

        query = select(OS)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))
        query = query.offset((page - 1) * limit).limit(limit)

        os = await self.session.scalars(query)
        return os.all()

    async def count(self, search: str | None = None) -> int:
        """Подсчитать количество ОС с поиском"""

        query = select(func.count()).select_from(OS)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))

        return await self.session.scalar(query) or 0

    async def get_by_id(self, os_id: int) -> OS | None:
        """Получить одну ОС по ID"""

        return await self.session.scalar(select(OS).where(OS.id == os_id))

    # Проверка связей

    async def has_computers(self, os_id: int) -> bool:
        """Проверить, есть ли компьютеры с данной ОС"""

        from app.models import Computer

        result = await self.session.scalar(
            select(exists().where(Computer.os_id == os_id))
        )
        return bool(result)

    # Изменение

    async def create(self, **kwargs: Any) -> OS:
        """Добавить новую ОС"""

        os = OS(**kwargs)
        self.session.add(os)
        await self.session.flush()
        await self.session.refresh(os)
        return os

    async def update(self, os: OS, **kwargs: Any) -> OS:
        """Обновить поля ОС"""

        for key, value in kwargs.items():
            setattr(os, key, value)
        await self.session.flush()
        await self.session.refresh(os)
        return os

    async def delete(self, os: OS) -> None:
        """Удалить ОС"""

        await self.session.delete(os)
        await self.session.flush()
