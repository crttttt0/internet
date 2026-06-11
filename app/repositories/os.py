from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import OS


class OSRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, skip: int, limit: int) -> Sequence[OS]:
        """Получить все операционные системы с пагинацией"""

        os_list = await self.session.scalars(select(OS).offset(skip).limit(limit))
        return os_list.all()

    async def get_by_id(self, os_id: int) -> OS | None:
        """Получить одну ОС по ID"""

        return await self.session.scalar(select(OS).where(OS.id == os_id))

    async def create(self, **kwargs: Any) -> OS:
        """Добавить новую ОС в сессию"""

        os = OS(**kwargs)
        self.session.add(os)
        await self.session.flush()
        await self.session.refresh(os)

        return os

    async def update(self, os: OS, **kwargs: Any) -> OS:
        """Обновить поля ОС из переданных kwargs"""

        for key, value in kwargs.items():
            setattr(os, key, value)
        await self.session.flush()
        await self.session.refresh(os)

        return os

    async def delete(self, os: OS) -> None:
        """Удалить ОС"""

        await self.session.delete(os)
        await self.session.flush()
