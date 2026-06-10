from typing import Any, Sequence, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_with_division(self, skip: int, limit: int) -> Sequence[User]:
        """Получить список пользователей с пагинацией и подразделениями."""

        users = await self.session.scalars(
            select(User).offset(skip).limit(limit).options(joinedload(User.division))
        )
        return users.all()

    async def get_by_id_with_division(self, user_id: int) -> User | None:
        """Получить одного пользователя по ID со связанным подразделением."""

        return await self.session.scalar(
            select(User).where(User.id == user_id).options(joinedload(User.division))
        )

    async def create(self, **kwargs: Any) -> User:
        """Добавить нового пользователя в сессию."""

        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return cast(User, await self.get_by_id_with_division(user.id))

    async def update(self, user: User, **kwargs: Any) -> User:
        """Обновить поля пользователя из переданных kwargs."""

        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.flush()
        return cast(User, await self.get_by_id_with_division(user.id))

    async def delete(self, user: User) -> None:
        """Пометить пользователя на удаление."""

        await self.session.delete(user)
        await self.session.flush()
