from typing import Sequence

from app.core.exceptions import EntityNotFoundException
from app.models import Vlan
from app.repositories import VlanRepository
from app.schemas.vlans import VlanCreate, VlanUpdate


class VlanService:
    def __init__(self, vlan_repository: VlanRepository) -> None:
        self.vlan_repository = vlan_repository

    async def _get_or_raise(self, vlan_id: int) -> Vlan:
        """Получить VLAN по ID или выбросить исключение"""

        db_vlan = await self.vlan_repository.get_by_id(vlan_id=vlan_id)
        if not db_vlan:
            raise EntityNotFoundException(f"VLAN с ID {vlan_id} не найден")
        return db_vlan

    async def _get_with_divisions_or_raise(self, vlan_id: int) -> Vlan:
        """Получить VLAN с подразделениями по ID или выбросить исключение"""

        db_vlan = await self.vlan_repository.get_by_id_with_divisions(
            vlan_id=vlan_id
        )
        if not db_vlan:
            raise EntityNotFoundException(f"VLAN с ID {vlan_id} не найден")
        return db_vlan

    async def get_by_id(self, vlan_id: int) -> Vlan:
        """Получить VLAN по ID"""

        return await self._get_or_raise(vlan_id=vlan_id)

    async def get_by_id_with_divisions(self, vlan_id: int) -> Vlan:
        """Получить VLAN по ID вместе с его подразделениями"""

        return await self._get_with_divisions_or_raise(vlan_id=vlan_id)

    async def get_all_with_divisions(self, skip: int, limit: int) -> Sequence[Vlan]:
        """Получить все VLAN-ы с пагинацией вместе с их подразделениями"""

        return await self.vlan_repository.get_all_with_divisions(
            skip=skip, limit=limit
        )

    async def create(self, vlan: VlanCreate) -> Vlan:
        """Создать новый VLAN"""

        return await self.vlan_repository.create(**vlan.model_dump())

    async def update(self, vlan_id: int, vlan: VlanUpdate) -> Vlan:
        """Обновить данные VLAN-а по ID"""

        db_vlan = await self._get_or_raise(vlan_id=vlan_id)
        return await self.vlan_repository.update(
            db_vlan, **vlan.model_dump(exclude_none=True)
        )

    async def delete(self, vlan_id: int) -> None:
        """Удалить VLAN по ID"""

        db_vlan = await self._get_or_raise(vlan_id=vlan_id)
        await self.vlan_repository.delete(vlan=db_vlan)
