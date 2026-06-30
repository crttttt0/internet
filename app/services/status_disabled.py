from app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
    InvalidForeignKeyException,
)
from app.models import StatusDisabled
from app.repositories import StatusDisabledRepository
from app.schemas.status_disabled import StatusDisabledCreate, StatusDisabledUpdate

from .computer import ComputerService


class StatusDisabledService:
    def __init__(
        self,
        status_disabled_repository: StatusDisabledRepository,
        computer_service: ComputerService,
    ) -> None:
        self.status_disabled_repository = status_disabled_repository
        self.computer_service = computer_service

    # Вспомогательные методы

    async def _get_by_computer_or_raise(self, computer_id: int) -> StatusDisabled:
        """Получить статус отключения по ID компьютера или выбросить исключение"""

        status = await self.status_disabled_repository.get_by_computer_id(
            computer_id=computer_id
        )
        if not status:
            raise EntityNotFoundException(
                f"Статус отключения для компьютера с ID {computer_id} не найден"
            )
        return status

    async def _check_computer_exists(self, computer_id: int) -> None:
        """Проверить, существует ли компьютер, если нет — выбросить исключение"""

        try:
            await self.computer_service.get_by_id(computer_id=computer_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(f"Компьютер с ID {computer_id} не найден")

    async def _check_status_not_exists(self, computer_id: int) -> None:
        """
        Проверить, что статуса отключения по ID компьютера не существует,
        выбросить исключение если существует
        """

        status = await self.status_disabled_repository.get_by_computer_id(
            computer_id=computer_id
        )
        if status:
            raise EntityAlreadyExistsException(
                f"Статус отключения для компьютера с ID {computer_id} уже существует"
            )

    # Получение

    async def get_by_computer_id(self, computer_id: int) -> StatusDisabled:
        """Получить статус отключения по ID компьютера"""

        return await self._get_by_computer_or_raise(computer_id=computer_id)

    # Изменение

    async def create(self, status: StatusDisabledCreate) -> StatusDisabled:
        """Создать статус отключения для компьютера"""

        await self._check_computer_exists(computer_id=status.computer_id)
        await self._check_status_not_exists(computer_id=status.computer_id)

        return await self.status_disabled_repository.create(**status.model_dump())

    async def update(
        self, computer_id: int, status: StatusDisabledUpdate
    ) -> StatusDisabled:
        """Обновить статус отключения по ID компьютера"""

        db_status = await self._get_by_computer_or_raise(computer_id=computer_id)
        return await self.status_disabled_repository.update(
            db_status, **status.model_dump(exclude_none=True)
        )

    async def delete(self, computer_id: int) -> None:
        """Удалить статус отключения по ID компьютера"""

        db_status = await self._get_by_computer_or_raise(computer_id=computer_id)
        await self.status_disabled_repository.delete(status=db_status)
