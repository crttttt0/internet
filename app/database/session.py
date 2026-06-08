from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .connection import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Выдает асинхронное подключение к БД.
    Коммит и роллбэк контролируются явно в бизнес-логике
    """

    async with AsyncSessionLocal() as session:
        yield session
