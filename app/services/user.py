from typing import Sequence

from app.core.exceptions import EntityNotFoundException
from app.core.security import hash_password
from app.models import User
from app.repositories import UserRepository
from app.schemas.users import UserCreate, UserUpdate
from app.services import DivisionService


class UserService:
    def __init__(
        self, user_repository: UserRepository, division_service: DivisionService
    ) -> None:
        self.user_repository = user_repository
        self.division_service = division_service

    async def _get_or_raise(self, user_id: int) -> User:
        """Получить пользователя по ID или выбросить исключение"""

        db_user = await self.user_repository.get_by_id(user_id=user_id)
        if not db_user:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} не найден")
        return db_user

    async def _get_with_division_or_raise(self, user_id: int) -> User:
        """Получить пользователя с подразделением по ID или выбросить исключение"""

        db_user = await self.user_repository.get_by_id_with_division(user_id=user_id)
        if not db_user:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} не найден")
        return db_user

    async def _check_division_exist(self, division_id: int) -> None:
        """Проверить, существует ли подразделение по ID, если нет — выбросить исключение"""

        await self.division_service.get_by_id(division_id=division_id)

    async def get_by_id(self, user_id: int) -> User:
        """Получить пользователя по ID"""

        return await self._get_or_raise(user_id=user_id)

    async def get_by_id_with_division(self, user_id: int) -> User:
        """Получить пользователя по ID вместе с подразделением"""

        return await self._get_with_division_or_raise(user_id=user_id)

    async def get_all_with_division(self, skip: int, limit: int) -> Sequence[User]:
        """Получить всех пользователей с пагинацией вместе с подразделениями"""

        return await self.user_repository.get_all_with_division(skip=skip, limit=limit)

    async def create(self, user: UserCreate) -> User:
        """Создать нового пользователя"""

        await self._check_division_exist(division_id=user.division_id)
        data = user.model_dump()
        data["domain_password"] = hash_password(data["domain_password"])

        return await self.user_repository.create(**data)

    async def update(self, user_id: int, user: UserUpdate) -> User:
        """Обновить данные пользователя по ID"""

        db_user = await self._get_or_raise(user_id=user_id)
        data = user.model_dump(exclude_none=True)
        if "division_id" in data:
            await self._check_division_exist(division_id=data["division_id"])
        if "domain_password" in data:
            data["domain_password"] = hash_password(data["domain_password"])

        return await self.user_repository.update(db_user, **data)

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя по ID"""

        db_user = await self._get_or_raise(user_id=user_id)
        await self.user_repository.delete(user=db_user)
