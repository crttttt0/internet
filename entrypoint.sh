#!/bin/sh
set -e

echo "Ожидаем доступности базы данных..."

python - <<'PYEOF'
import asyncio
import sys

from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def wait_for_db():
    url = settings.database.URL.get_secret_value()
    engine = create_async_engine(url)
    for attempt in range(30):
        try:
            async with engine.connect() as conn:
                pass
            print("База данных доступна")
            return
        except Exception as exc:
            print(f"БД пока не доступна ({attempt + 1}/30): {exc}")
            await asyncio.sleep(2)
    print("Не удалось подключиться к базе данных")
    sys.exit(1)

asyncio.run(wait_for_db())
PYEOF

echo "Применяем миграции базы данных..."
alembic upgrade head

echo "Заполняем начальные данные..."
python - <<'PYEOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

async def seed():
    url = settings.database.URL.get_secret_value()
    engine = create_async_engine(url)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM divisions"))
        count = result.scalar()
        if count == 0:
            print("Таблицы пустые, вставляем данные...")
            with open("/app/data.sql", "r") as f:
                sql = f.read()
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement:
                    await conn.execute(text(statement))
            await conn.commit()
            print("Данные вставлены")
        else:
            print(f"Данные уже есть ({count} записей в divisions), пропускаем")

asyncio.run(seed())
PYEOF

echo "Запускаем приложение..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
