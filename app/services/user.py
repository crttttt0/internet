from datetime import date
from typing import Sequence

from app.core.exceptions import (
    BusinessRuleViolationException,
    EntityNotFoundException,
    InvalidForeignKeyException,
)
from app.core.security import hash_password
from app.models import User
from app.repositories import UserRepository
from app.schemas.users import UserCreate, UserUpdate

from .division import DivisionService


class UserService:
    def __init__(
        self, user_repository: UserRepository, division_service: DivisionService
    ) -> None:
        self.user_repository = user_repository
        self.division_service = division_service

    # Вспомогательные методы

    async def _get_or_raise(self, user_id: int) -> User:
        """Получить пользователя по ID или выбросить исключение"""

        db_user = await self.user_repository.get_by_id(user_id=user_id)
        if not db_user:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} не найден")
        return db_user

    async def _get_with_relations_or_raise(self, user_id: int) -> User:
        """Получить пользователя с подразделением по ID или выбросить исключение"""

        db_user = await self.user_repository.get_by_id_with_relations(user_id=user_id)
        if not db_user:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} не найден")
        return db_user

    async def _check_division_exists(self, division_id: int) -> None:
        """Проверить существование подразделения, если нет — выбросить исключение"""

        try:
            await self.division_service.get_by_id(division_id=division_id)
        except EntityNotFoundException:
            raise InvalidForeignKeyException(
                f"Подразделение с ID {division_id} не найдено"
            )

    # Получение

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[User], int]:
        """Получить всех пользователей с пагинацией и поиском по ФИО"""

        items = await self.user_repository.get_all_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.user_repository.count(search=search)

        return items, total

    async def get_all_with_relations_search_filters(
        self,
        page: int,
        limit: int,
        division_id: int | None = None,
        email: str | None = None,
        phone: str | None = None,
        input_date_from: date | None = None,
        input_date_to: date | None = None,
        search: str | None = None,
    ) -> tuple[Sequence[User], int]:
        """Получить всех пользователей с подразделением, пагинацией, фильтрами и поиском"""

        items = await self.user_repository.get_all_with_relations_search_filters(
            page=page,
            limit=limit,
            division_id=division_id,
            email=email,
            phone=phone,
            input_date_from=input_date_from,
            input_date_to=input_date_to,
            search=search,
        )
        total = await self.user_repository.count(
            division_id=division_id,
            email=email,
            phone=phone,
            input_date_from=input_date_from,
            input_date_to=input_date_to,
            search=search,
        )

        return items, total

    async def get_by_id(self, user_id: int) -> User:
        """Получить пользователя по ID"""

        return await self._get_or_raise(user_id=user_id)

    async def get_by_id_with_relations(self, user_id: int) -> User:
        """Получить пользователя по ID с подразделением"""

        return await self._get_with_relations_or_raise(user_id=user_id)

    # Получение фильтров

    async def get_all_emails_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные email с пагинацией и поиском"""

        items = await self.user_repository.get_all_emails_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.user_repository.count_emails(search=search)

        return items, total

    async def get_all_phones_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> tuple[Sequence[str], int]:
        """Получить все уникальные телефоны с пагинацией и поиском"""

        items = await self.user_repository.get_all_phones_with_search(
            page=page, limit=limit, search=search
        )
        total = await self.user_repository.count_phones(search=search)

        return items, total

    # Изменение

    async def create(self, user: UserCreate) -> User:
        """Создать нового пользователя"""

        await self._check_division_exists(division_id=user.division_id)
        data = user.model_dump()
        data["domain_password"] = hash_password(data["domain_password"])

        return await self.user_repository.create(**data)

    async def update(self, user_id: int, user: UserUpdate) -> User:
        """Обновить данные пользователя по ID"""

        db_user = await self._get_or_raise(user_id=user_id)
        data = user.model_dump(exclude_none=True)

        if "division_id" in data:
            await self._check_division_exists(division_id=data["division_id"])
        if "domain_password" in data:
            data["domain_password"] = hash_password(data["domain_password"])

        return await self.user_repository.update(db_user, **data)

    async def delete(self, user_id: int) -> None:
        """Удалить пользователя по ID"""

        db_user = await self._get_or_raise(user_id=user_id)

        if await self.user_repository.has_computers(user_id=user_id):
            raise BusinessRuleViolationException(
                f"Невозможно удалить пользователя с ID {user_id}: есть привязанные компьютеры"
            )

        await self.user_repository.delete(user=db_user)
