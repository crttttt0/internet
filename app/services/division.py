from typing import Sequence

from app.core.exceptions import EntityNotFoundException
from app.models import Division
from app.repositories import DivisionRepository
from app.schemas.divisions import DivisionCreate, DivisionUpdate


class DivisionService:
    def __init__(self, division_repository: DivisionRepository) -> None:
        self.division_repository = division_repository

    async def _get_or_raise(self, division_id: int) -> Division:
        """Получить подразделение по ID или выбросить исключение"""

        db_division = await self.division_repository.get_by_id(division_id=division_id)
        if not db_division:
            raise EntityNotFoundException(
                f"Подразделение с ID {division_id} не найдено"
            )
        return db_division

    async def _get_with_vlans_or_raise(self, division_id: int) -> Division:
        """Получить подразделение с VLAN-ами по ID или выбросить исключение"""

        db_division = await self.division_repository.get_by_id_with_vlan(
            division_id=division_id
        )
        if not db_division:
            raise EntityNotFoundException(
                f"Подразделение с ID {division_id} не найдено"
            )
        return db_division

    async def get_by_id(self, division_id: int) -> Division:
        """Получить подразделение по ID"""

        return await self._get_or_raise(division_id=division_id)

    async def get_by_id_with_vlans(self, division_id: int) -> Division:
        """Получить подразделение по ID вместе с его VLAN-ами"""

        return await self._get_with_vlans_or_raise(division_id=division_id)

    async def get_all_with_vlans(self, skip: int, limit: int) -> Sequence[Division]:
        """Получить все подразделения с пагинацией вместе с их VLAN-ами"""

        return await self.division_repository.get_all_with_vlan(skip=skip, limit=limit)

    async def create(self, division: DivisionCreate) -> Division:
        """Создать новое подразделение"""

        return await self.division_repository.create(**division.model_dump())

    async def update(self, division_id: int, division: DivisionUpdate) -> Division:
        """Обновить данные подразделения по ID"""

        db_division = await self._get_or_raise(division_id=division_id)
        return await self.division_repository.update(
            db_division, **division.model_dump(exclude_none=True)
        )

    async def delete(self, division_id: int) -> None:
        """Удалить подразделение по ID"""

        db_division = await self._get_or_raise(division_id=division_id)
        await self.division_repository.delete(division=db_division)
