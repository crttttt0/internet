from typing import Sequence

from app.core.exceptions import EntityNotFoundException
from app.models import OS
from app.repositories import OSRepository
from app.schemas.os import OSCreate, OSUpdate


class OSService:
    def __init__(self, os_repository: OSRepository) -> None:
        self.os_repository = os_repository

    async def _get_or_raise(self, os_id: int) -> OS:
        """Получить ОС по ID или выбросить исключение"""

        db_os = await self.os_repository.get_by_id(os_id=os_id)
        if not db_os:
            raise EntityNotFoundException(f"ОС с ID {os_id} не найдена")
        return db_os

    async def get_by_id(self, os_id: int) -> OS:
        """Получить ОС по ID"""

        return await self._get_or_raise(os_id=os_id)

    async def get_all(self, skip: int, limit: int) -> Sequence[OS]:
        """Получить все ОС с пагинацией"""

        return await self.os_repository.get_all(skip=skip, limit=limit)

    async def create(self, os: OSCreate) -> OS:
        """Создать новую ОС"""

        return await self.os_repository.create(**os.model_dump())

    async def update(self, os_id: int, os: OSUpdate) -> OS:
        """Обновить данные ОС по ID"""

        db_os = await self._get_or_raise(os_id=os_id)
        return await self.os_repository.update(
            db_os, **os.model_dump(exclude_none=True)
        )

    async def delete(self, os_id: int) -> None:
        """Удалить ОС по ID"""

        db_os = await self._get_or_raise(os_id=os_id)
        await self.os_repository.delete(os=db_os)
