from typing import Any, Sequence, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Division


class DivisionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_with_vlan(self, skip: int, limit: int) -> Sequence[Division]:
        """Получить все подразделения с пагинацией"""

        divisions = await self.session.scalars(
            select(Division)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Division.vlans))
        )
        return divisions.all()

    async def get_by_id(self, division_id: int) -> Division | None:
        """Получить одно подразделение по ID"""

        return await self.session.scalar(
            select(Division).where(Division.id == division_id)
        )

    async def get_by_id_with_vlan(self, division_id: int) -> Division | None:
        """Получить одно подразделение по ID вместе с его VLAN-ами"""

        return await self.session.scalar(
            select(Division)
            .where(Division.id == division_id)
            .options(selectinload(Division.vlans))
        )

    async def create(self, **kwargs: Any) -> Division:
        """Добавить новое подразделение в сессию"""

        division = Division(**kwargs)
        self.session.add(division)
        await self.session.flush()
        return cast(Division, await self.get_by_id_with_vlan(division.id))

    async def update(self, division: Division, **kwargs: Any) -> Division:
        """Обновить поля подразделения из переданных kwargs"""

        for key, value in kwargs.items():
            setattr(division, key, value)
        await self.session.flush()
        return cast(Division, await self.get_by_id_with_vlan(division.id))

    async def delete(self, division: Division) -> None:
        """Удалить подразделение."""

        await self.session.delete(division)
        await self.session.flush()
