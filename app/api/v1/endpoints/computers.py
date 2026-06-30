from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_computer_service
from app.schemas.computers import (
    ComputerCreate,
    ComputerFilters,
    ComputerFullRead,
    ComputerRead,
    ComputerUpdate,
)
from app.schemas.filters import FilterOption
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services import ComputerService

router = APIRouter(prefix="/computers", tags=["computers"])


# Получение


@router.get(
    "/",
    response_model=PaginatedResponse[ComputerRead],
    summary="Список компьютеров (пагинация, поиск)",
    operation_id="getAllComputers",
)
async def get_all_computers_with_search(
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=255, description="Поиск по имени")
    ] = None,
) -> PaginatedResponse[ComputerRead]:
    """
    Возвращает список компьютеров с пагинацией и поиском по имени и описанию.
    Связи не загружаются — использовать GET /computers/full для полных данных.

    - **200** — список компьютеров (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await computer_service.get_all_with_search(
        **pagination.model_dump(),
        search=search,
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=PaginatedResponse[ComputerFullRead],
    summary="Список компьютеров со связями (пагинация, поиск, фильтры)",
    operation_id="getAllComputersFull",
)
async def get_all_computers_full(
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[ComputerFilters, Depends()],
) -> PaginatedResponse[ComputerFullRead]:
    """
    Возвращает список компьютеров с загруженными связями (подразделение, пользователь, ОС, статус отключения).
    Поддерживает фильтрацию по корпусу, комнате, подразделению, ОС, VLAN, пользователю и статусу отключения.

    - **200** — список компьютеров (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """
    items, total = await computer_service.get_all_with_relations_search_filters(
        **pagination.model_dump(), **filters.model_dump()
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


# Получение фильтров


@router.get(
    "/buildings",
    response_model=PaginatedResponse[FilterOption],
    summary="Список корпусов компьютеров для фильтра (пагинация, поиск)",
    operation_id="getAllComputerBuildingsFilter",
    tags=["filters"],
)
async def get_all_computer_buildings(
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=255, description="Поиск по корпусу")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных корпусов, в которых зарегистрированы компьютеры.

    - **200** — список корпусов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await computer_service.get_all_buildings_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


@router.get(
    "/rooms",
    response_model=PaginatedResponse[FilterOption],
    summary="Список комнат компьютеров для фильтра (пагинация, поиск)",
    operation_id="getAllComputerRoomsFilter",
    tags=["filters"],
)
async def get_all_computer_rooms(
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=255, description="Поиск по комнате")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных комнат, в которых зарегистрированы компьютеры.

    - **200** — список комнат (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await computer_service.get_all_rooms_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


# Получение по ID


@router.get(
    "/{computer_id}",
    response_model=ComputerRead,
    summary="Компьютер по ID",
    operation_id="getComputerById",
)
async def get_computer_by_id(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerRead:
    """
    Возвращает компьютер по ID без загрузки связей.
    Для полных данных использовать `GET /computers/{computer_id}/full`.

    - **200** — компьютер найден
    - **404** — компьютер с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await computer_service.get_by_id(computer_id=computer_id)  # type: ignore[return-value]


@router.get(
    "/{computer_id}/full",
    response_model=ComputerFullRead,
    summary="Компьютер по ID со связями",
    operation_id="getComputerByIdFull",
)
async def get_computer_by_id_full(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerFullRead:
    """
    Возвращает компьютер по ID с загруженными связями: подразделение, пользователь, ОС, статус отключения.

    - **200** — компьютер найден
    - **404** — компьютер с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await computer_service.get_by_id_with_relations(computer_id=computer_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=ComputerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать компьютер",
    operation_id="createComputer",
)
async def create_computer(
    computer: ComputerCreate,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerRead:
    """
    Создаёт новый компьютер.

    - **201** — компьютер создан, возвращает объект с присвоенным `id`
    - **400** — подразделение с указанным `division_id` не существует; или пользователь с указанным `user_id` не существует; или ОС с указанным `os_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await computer_service.create(computer=computer)  # type: ignore[return-value]


@router.patch(
    "/{computer_id}",
    response_model=ComputerRead,
    summary="Обновить компьютер",
    operation_id="updateComputer",
)
async def update_computer(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    computer: ComputerUpdate,
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> ComputerRead:
    """
    Обновляет поля компьютера по ID. Передавать только те поля, которые нужно изменить.

    - **200** — компьютер обновлён
    - **400** — подразделение с указанным `division_id` не существует; или пользователь с указанным `user_id` не существует; или ОС с указанным `os_id` не существует
    - **404** — компьютер с таким ID не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await computer_service.update(computer_id=computer_id, computer=computer)  # type: ignore[return-value]


@router.delete(
    "/{computer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить компьютер",
    operation_id="deleteComputer",
)
async def delete_computer(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    computer_service: Annotated[ComputerService, Depends(get_computer_service)],
) -> None:
    """
    Удаляет компьютер по ID. Тело ответа при успехе отсутствует.

    - **204** — компьютер удалён
    - **404** — компьютер с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    await computer_service.delete(computer_id=computer_id)
