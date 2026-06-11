from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_computer_service
from app.schemas.computers import (
    ComputerCreate,
    ComputerFilters,
    ComputerFullRead,
    ComputerRead,
    ComputerUpdate,
)
from app.services import ComputerService

router = APIRouter(prefix="/computers", tags=["computers"])


@router.get("/", response_model=list[ComputerRead], summary="Список всех компьютеров")
async def get_all_computers(
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Максимальное количество записей в ответе"),
    ] = 24,
) -> Sequence[ComputerRead]:
    """
    Возвращает список всех компьютеров с пагинацией без джойнов.

    - **200** — список компьютеров (может быть пустым)
    """

    return await computer_service.get_all(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=list[ComputerFullRead],
    summary="Список всех компьютеров со связями и фильтрами",
)
async def get_all_with_relations_search_filters(
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
    filters: Annotated[ComputerFilters, Depends()],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Максимальное количество записей")
    ] = 24,
) -> Sequence[ComputerFullRead]:
    return await computer_service.get_all_with_relations_search_filters(
        skip=skip, limit=limit, filters=filters
    )  # type: ignore[return-value]


@router.get("/{computer_id}", response_model=ComputerRead, summary="Компьютер по ID")
async def get_computer_by_id(
    computer_id: int,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerRead:
    """
    Возвращает компьютер по ID без джойнов.

    - **200** — компьютер найден
    - **404** — компьютер с таким ID не существует
    """

    return await computer_service.get_by_id(computer_id)  # type: ignore[return-value]


@router.get(
    "/{computer_id}/full",
    response_model=ComputerFullRead,
    summary="Компьютер по ID со связями",
)
async def get_computer_by_id_with_relations(
    computer_id: int,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerFullRead:
    """
    Возвращает компьютер по ID с развёрнутыми пользователем, ОС и статусом отключения.

    - **200** — компьютер найден
    - **404** — компьютер с таким ID не существует
    """

    return await computer_service.get_by_id_with_relations(computer_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=ComputerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать компьютер",
)
async def create_computer(
    computer: ComputerCreate,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerRead:
    """
    Создаёт новый компьютер.

    - **201** — компьютер создан, возвращает объект с присвоенным `id`
    - **404** — подразделение с указанным `division_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await computer_service.create(computer)  # type: ignore[return-value]


@router.patch(
    "/{computer_id}", response_model=ComputerRead, summary="Обновить компьютер"
)
async def update_computer(
    computer_id: int,
    computer: ComputerUpdate,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerRead:
    """
    Обновляет поля компьютера по ID. Передавать только те поля, которые нужно изменить.

    - **200** — компьютер обновлён
    - **404** — компьютер с таким ID не существует, или подразделение с указанным `division_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await computer_service.update(computer_id, computer)  # type: ignore[return-value]


@router.delete(
    "/{computer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить компьютер",
)
async def delete_computer(
    computer_id: int,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> None:
    """
    Удаляет компьютер по ID. Тело ответа при успехе отсутствует.

    - **204** — компьютер удалён
    - **404** — компьютер с таким ID не существует
    """

    await computer_service.delete(computer_id)
