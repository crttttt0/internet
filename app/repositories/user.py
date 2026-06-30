from datetime import date
from typing import Any, Sequence, cast

from sqlalchemy import ColumnElement, Select, distinct, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Вспомогательные методы

    def _build_search_condition(self, search: str) -> ColumnElement[bool]:
        """Условие поиска по ФИО"""

        return or_(
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.patronymic.ilike(f"%{search}%"),
        )

    def _build_search_and_filter_conditions(
        self,
        division_id: int | None = None,
        email: str | None = None,
        phone: str | None = None,
        input_date_from: date | None = None,
        input_date_to: date | None = None,
        search: str | None = None,
    ) -> list[ColumnElement[bool]]:
        """Собрать список условий WHERE из переданных фильтров"""

        conditions = []

        if division_id is not None:
            conditions.append(User.division_id == division_id)
        if email is not None:
            conditions.append(User.email == email)
        if phone is not None:
            conditions.append(User.phone == phone)
        if input_date_from is not None:
            conditions.append(User.input_date >= input_date_from)
        if input_date_to is not None:
            conditions.append(User.input_date <= input_date_to)
        if search is not None:
            conditions.append(self._build_search_condition(search=search))

        return conditions

    def _base_query_with_relations(self) -> Select[tuple[User]]:
        """Базовый SELECT с загрузкой подразделения"""

        return select(User).options(joinedload(User.division))

    # Получение/подсчет

    async def get_all_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[User]:
        """Получить всех пользователей с пагинацией и поиском по ФИО"""

        query = select(User)
        if search is not None:
            query = query.where(self._build_search_condition(search=search))
        query = query.offset((page - 1) * limit).limit(limit)

        return (await self.session.scalars(query)).all()

    async def count(
        self,
        division_id: int | None = None,
        email: str | None = None,
        phone: str | None = None,
        input_date_from: date | None = None,
        input_date_to: date | None = None,
        search: str | None = None,
    ) -> int:
        """Подсчитать количество пользователей с фильтрами"""

        conditions = self._build_search_and_filter_conditions(
            division_id=division_id,
            email=email,
            phone=phone,
            input_date_from=input_date_from,
            input_date_to=input_date_to,
            search=search,
        )
        query = select(func.count()).select_from(User)
        if conditions:
            query = query.where(*conditions)

        return await self.session.scalar(query) or 0

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
    ) -> Sequence[User]:
        """Получить всех пользователей с подразделением, пагинацией, фильтрами и поиском"""

        conditions = self._build_search_and_filter_conditions(
            division_id=division_id,
            email=email,
            phone=phone,
            input_date_from=input_date_from,
            input_date_to=input_date_to,
            search=search,
        )
        query = self._base_query_with_relations()
        if conditions:
            query = query.where(*conditions)
        query = query.offset((page - 1) * limit).limit(limit)

        return (await self.session.scalars(query)).all()

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить одного пользователя по ID"""

        return await self.session.scalar(select(User).where(User.id == user_id))

    async def get_by_id_with_relations(self, user_id: int) -> User | None:
        """Получить одного пользователя по ID с подразделением"""

        return await self.session.scalar(
            self._base_query_with_relations().where(User.id == user_id)
        )

    # Получение/подсчет полей сущности

    async def count_emails(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных email с поиском"""

        query = select(func.count(distinct(User.email))).where(User.email.is_not(None))
        if search is not None:
            query = query.where(User.email.ilike(f"%{search}%"))

        return await self.session.scalar(query) or 0

    # Получение/Подсчет полей сущности

    async def get_all_emails_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные email с поиском"""

        query = select(User.email).distinct().where(User.email.is_not(None))
        if search is not None:
            query = query.where(User.email.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)

        return cast(Sequence[str], (await self.session.scalars(query)).all())

    async def count_phones(self, search: str | None = None) -> int:
        """Подсчитать количество уникальных телефонов с поиском"""

        query = select(func.count(distinct(User.phone))).where(User.phone.is_not(None))
        if search is not None:
            query = query.where(User.phone.ilike(f"%{search}%"))

        return await self.session.scalar(query) or 0

    async def get_all_phones_with_search(
        self, page: int, limit: int, search: str | None = None
    ) -> Sequence[str]:
        """Получить все уникальные телефоны с поиском"""

        query = select(User.phone).distinct().where(User.phone.is_not(None))
        if search is not None:
            query = query.where(User.phone.ilike(f"%{search}%"))
        query = query.offset((page - 1) * limit).limit(limit)

        return cast(Sequence[str], (await self.session.scalars(query)).all())

    # Проверка связей

    async def has_computers(self, user_id: int) -> bool:
        """Проверить, есть ли компьютеры привязанные к пользователю"""

        from app.models import Computer

        result = await self.session.scalar(
            select(exists().where(Computer.user_id == user_id))
        )
        return bool(result)

    # Изменение

    async def create(self, **kwargs: Any) -> User:
        """Добавить нового пользователя"""

        user = User(**kwargs)
        self.session.add(user)
        await self.session.flush()
        return cast(User, await self.get_by_id(user.id))

    async def update(self, user: User, **kwargs: Any) -> User:
        """Обновить поля пользователя"""

        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.session.flush()
        return cast(User, await self.get_by_id(user.id))

    async def delete(self, user: User) -> None:
        """Удалить пользователя"""

        await self.session.delete(user)
        await self.session.flush()
