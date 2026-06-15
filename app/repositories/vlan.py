from typing import Any, Sequence, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Vlan


class VlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_with_divisions(self, skip: int, limit: int) -> Sequence[Vlan]:
        """Получить все VLAN-ы с пагинацией вместе с их подразделениями"""

        vlans = await self.session.scalars(
            select(Vlan).offset(skip).limit(limit).options(selectinload(Vlan.divisions))
        )
        return vlans.all()

    async def get_by_id(self, vlan_id: int) -> Vlan | None:
        """Получить один VLAN по ID"""

        return await self.session.scalar(select(Vlan).where(Vlan.id == vlan_id))

    async def get_by_id_with_divisions(self, vlan_id: int) -> Vlan | None:
        """Получить один VLAN по ID вместе с его подразделениями"""

        return await self.session.scalar(
            select(Vlan).where(Vlan.id == vlan_id).options(selectinload(Vlan.divisions))
        )

    async def create(self, **kwargs: Any) -> Vlan:
        """Добавить новый VLAN в сессию"""

        vlan = Vlan(**kwargs)
        self.session.add(vlan)
        await self.session.flush()
        return cast(Vlan, await self.get_by_id_with_divisions(vlan.id))

    async def update(self, vlan: Vlan, **kwargs: Any) -> Vlan:
        """Обновить поля VLAN-а из переданных kwargs"""

        for key, value in kwargs.items():
            setattr(vlan, key, value)
        await self.session.flush()
        return cast(Vlan, await self.get_by_id_with_divisions(vlan.id))

    async def delete(self, vlan: Vlan) -> None:
        """Удалить VLAN"""

        await self.session.delete(vlan)
        await self.session.flush()
