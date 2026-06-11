from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import StatusDisabled


class StatusDisabledRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_computer_id(self, computer_id: int) -> StatusDisabled | None:
        """Получить статус отключения по ID компьютера"""

        return await self.session.scalar(
            select(StatusDisabled).where(StatusDisabled.computer_id == computer_id)
        )

    async def create(self, **kwargs: Any) -> StatusDisabled:
        """Добавить новый статус отключения в сессию"""

        status = StatusDisabled(**kwargs)
        self.session.add(status)
        await self.session.flush()
        await self.session.refresh(status)

        return status

    async def update(self, status: StatusDisabled, **kwargs: Any) -> StatusDisabled:
        """Обновить поля статуса отключения из переданных kwargs"""

        for key, value in kwargs.items():
            setattr(status, key, value)
        await self.session.flush()
        await self.session.refresh(status)

        return status

    async def delete(self, status: StatusDisabled) -> None:
        """Удалить статус отключения"""

        await self.session.delete(status)
        await self.session.flush()
