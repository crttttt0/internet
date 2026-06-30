from typing import Sequence

from app.core.exceptions import EntityNotFoundException, InvalidForeignKeyException
from app.models import Computer
from app.repositories import ComputerRepository
from app.schemas.computers import ComputerCreate, ComputerUpdate

from .division import DivisionService
from .os import OSService
from .user import UserService


class ComputerService:
    def __init__(
        self,
        computer_repository: ComputerRepository,
        division_service: DivisionService,
        user_service: UserService,
        os_service: OSService,
    ) -> None:
        self.computer_repository = computer_repository
        self.division_service = division_service
        self.user_service = user_service
        self.os_service = os_service

    # Вспомогательные методы

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

        try:
            await self.division_service.get_by_id(division_id=division_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(
                f"Подразделение с ID {division_id} не найдено"
            )

    async def _check_user_exists(self, user_id: int) -> None:
        """Проверить, существует ли пользователь, если нет — выбросить исключение"""

        try:
            await self.user_service.get_by_id(user_id=user_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(f"Пользователь с ID {user_id} не найден")

    async def _check_os_exists(self, os_id: int) -> None:
        """Проверить, существует ли ОС, если нет — выбросить исключение"""

        try:
            await self.os_service.get_by_id(os_id=os_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(f"ОС с ID {os_id} не найдена")

    # Получение

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[Computer], int]:
        """Получить все компьютеры с пагинацией и поиском"""
        items = await self.computer_repository.get_all_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.computer_repository.count(search=search)

        return items, total

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        build: str | None = None,
        pc_room: str | None = None,
        division_id: int | None = None,
        os_id: int | None = None,
        vlan_id: int | None = None,
        user_id: int | None = None,
        is_disabled: bool | None = None,
        search: str | None = None,
    ) -> tuple[Sequence[Computer], int]:
        """Получить все компьютеры с пагинацией, связями и фильтрами"""
        items = await self.computer_repository.get_all_with_relations_search_filters(
            page=page,
            limit=limit,
            build=build,
            pc_room=pc_room,
            division_id=division_id,
            os_id=os_id,
            vlan_id=vlan_id,
            user_id=user_id,
            is_disabled=is_disabled,
            search=search,
        )
        total = await self.computer_repository.count(
            build=build,
            pc_room=pc_room,
            division_id=division_id,
            os_id=os_id,
            vlan_id=vlan_id,
            user_id=user_id,
            is_disabled=is_disabled,
            search=search,
        )
        return items, total

    async def get_by_id(self, computer_id: int) -> Computer:
        """Получить компьютер по ID"""

        return await self._get_or_raise(computer_id=computer_id)

    async def get_by_id_with_relations(self, computer_id: int) -> Computer:
        """Получить компьютер по ID со всеми связями"""

        return await self._get_with_relations_or_raise(computer_id=computer_id)

    # Получение фильтров

    async def get_all_buildings_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все корпусы с пагинацией и поиском"""

        items = await self.computer_repository.get_all_buildings_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.computer_repository.count_buildings(search=search)

        return items, total

    async def get_all_rooms_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все комнаты с пагинацией и поиском"""

        items = await self.computer_repository.get_all_rooms_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.computer_repository.count_rooms(search=search)

        return items, total

    # Изменение

    async def create(self, computer: ComputerCreate) -> Computer:
        """Создать новый компьютер"""

        await self._check_division_exists(division_id=computer.division_id)

        if computer.user_id is not None:
            await self._check_user_exists(user_id=computer.user_id)
        if computer.os_id is not None:
            await self._check_os_exists(os_id=computer.os_id)

        return await self.computer_repository.create(**computer.model_dump())

    async def update(self, computer_id: int, computer: ComputerUpdate) -> Computer:
        """Обновить данные компьютера по ID"""

        db_computer = await self._get_or_raise(computer_id=computer_id)
        data = computer.model_dump(exclude_none=True)

        if "division_id" in data:
            await self._check_division_exists(division_id=data["division_id"])
        if "user_id" in data:
            await self._check_user_exists(user_id=data["user_id"])
        if "os_id" in data:
            await self._check_os_exists(os_id=data["os_id"])

        return await self.computer_repository.update(db_computer, **data)

    async def delete(self, computer_id: int) -> None:
        """Удалить компьютер по ID"""

        db_computer = await self._get_or_raise(computer_id=computer_id)
        await self.computer_repository.delete(computer=db_computer)
