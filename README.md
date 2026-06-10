# Internet

REST API для управления сотрудниками, подразделениями и сетевой инфраструктурой.

## Стек

- **Python 3.14**,
- FastAPI
- SQLAlchemy 2.0 (async)
- Alembic
- MySQL

## Требования

- Python 3.14+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- MySQL 8+

## Запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/crttttt0/internet.git)
cd internet
```

### 2. Установить зависимости

```bash
uv sync
```

### 3. Настроить переменные окружения

Скопировать `.env.example` и заполнить своими значениями:

```bash
cp .env.example .env
```

```env
DATABASE__URL=mysql+aiomysql://<user>:<password>@<host>:<port>/<db_name>
JWT__SECRET_KEY=<случайная строка>
```

### 4. Применить миграции

```bash
uv run alembic upgrade head
```

### 5. Запустить сервер

```bash
uv run uvicorn app.main:app --reload
```

API будет доступно по адресу: `http://localhost:8000`

Документация: `http://localhost:8000/docs`

## Разработка

Линтер и форматтер:

```bash
uv run ruff check .
uv run ruff check --select I --fix .
uv run ruff format .
```

Создать новую миграцию:

```bash
uv run alembic revision --autogenerate -m "описание"
```
