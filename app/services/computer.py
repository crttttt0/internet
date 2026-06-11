from typing import Sequence

from app.core.exceptions import EntityNotFoundException
from app.models import Computer
from app.repositories import ComputerRepository
from app.schemas.computers import ComputerCreate, ComputerFilters, ComputerUpdate

from .division import DivisionService


class ComputerService:
    def __init__(
        self,
        computer_repository: ComputerRepository,
        division_service: DivisionService,
    ) -> None:
        self.computer_repository = computer_repository
        self.division_service = division_service

    async def _get_or_raise(self, computer_id: int) -> Computer:
        """Получить компьютер по ID или выбросить исключение"""

        db_computer = await self.computer_repository.get_by_id(computer_id=computer_id)
        if not db_computer:
            raise EntityNotFoundException(f"Компьютер с ID {computer_id} не найден")
        return db_computer

    async def _get_with_relations_or_raise(self, computer_id: int) -> Computer:
        """Получить компьютер со всеми связями по ID или выбросить исключение"""

        db_computer = await self.computer_repository.get_by_id_with_relations(
            computer_id=computer_id
        )
        if not db_computer:
            raise EntityNotFoundException(f"Компьютер с ID {computer_id} не найден")
        return db_computer

    async def _check_division_exists(self, division_id: int) -> None:
        """Проверить, существует ли подразделение, если нет — выбросить исключение"""

        await self.division_service.get_by_id(division_id=division_id)

    async def get_all(self, skip: int, limit: int) -> Sequence[Computer]:
        """Получить все компьютеры с пагинацией"""

        return await self.computer_repository.get_all(skip=skip, limit=limit)

    async def get_all_with_relations_search_filters(
        self, skip: int, limit: int, filters: ComputerFilters
    ) -> Sequence[Computer]:
        """Получить все компьютеры с пагинацией и всеми связями"""

        return await self.computer_repository.get_all_with_relations_search_filters(
            skip=skip, limit=limit, **filters.model_dump()
        )

    async def get_by_id(self, computer_id: int) -> Computer:
        """Получить компьютер по ID"""

        return await self._get_or_raise(computer_id=computer_id)

    async def get_by_id_with_relations(self, computer_id: int) -> Computer:
        """Получить компьютер по ID со всеми связями"""

        return await self._get_with_relations_or_raise(computer_id=computer_id)

    async def create(self, computer: ComputerCreate) -> Computer:
        """Создать новый компьютер"""

        await self._check_division_exists(division_id=computer.division_id)
        return await self.computer_repository.create(**computer.model_dump())

    async def update(self, computer_id: int, computer: ComputerUpdate) -> Computer:
        """Обновить данные компьютера по ID"""

        db_computer = await self._get_or_raise(computer_id=computer_id)
        data = computer.model_dump(exclude_none=True)
        if "division_id" in data:
            await self._check_division_exists(division_id=data["division_id"])
        return await self.computer_repository.update(db_computer, **data)

    async def delete(self, computer_id: int) -> None:
        """Удалить компьютер по ID"""

        db_computer = await self._get_or_raise(computer_id=computer_id)
        await self.computer_repository.delete(computer=db_computer)
