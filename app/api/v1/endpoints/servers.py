from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_server_service
from app.schemas.filters import FilterOption
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.servers import (
    ServerCreate,
    ServerFilters,
    ServerFullRead,
    ServerRead,
    ServerUpdate,
)
from app.services import ServerService

router = APIRouter(prefix="/servers", tags=["servers"])


# Получение


@router.get(
    "/",
    response_model=PaginatedResponse[ServerRead],
    summary="Список серверов (пагинация, поиск)",
    operation_id="getAllServers",
)
async def get_all_servers(
    server_service: Annotated[ServerService, Depends(get_server_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по IP и MAC-адресу")
    ] = None,
) -> PaginatedResponse[ServerRead]:
    """
    Возвращает список серверов с пагинацией и поиском по IP и MAC-адресу.
    Связи не загружаются — использовать GET /servers/full для данных с подразделением и VLAN-ами.

    - **200** — список серверов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await server_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=PaginatedResponse[ServerFullRead],
    summary="Список серверов с подразделением и VLAN-ами (пагинация, поиск, фильтры)",
    operation_id="getAllServersFull",
)
async def get_all_servers_full(
    server_service: Annotated[ServerService, Depends(get_server_service)],
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[ServerFilters, Depends()],
) -> PaginatedResponse[ServerFullRead]:
    """
    Возвращает список серверов с загруженным подразделением и VLAN-ами.
    Поддерживает фильтрацию по комнате, корпусу, подразделению, администратору и диапазону дат.

    - **200** — список серверов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await server_service.get_all_with_relations_search_filters(
        **pagination.model_dump(), **filters.model_dump()
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


# Получение фильтров


@router.get(
    "/builds",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных корпусов серверов для фильтра (пагинация, поиск)",
    operation_id="getAllServerBuildsFilter",
    tags=["filters"],
)
async def get_all_server_builds(
    server_service: Annotated[ServerService, Depends(get_server_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по корпусу")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных корпусов, в которых зарегистрированы серверы.

    - **200** — список корпусов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await server_service.get_all_builds_with_search(
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
    summary="Список уникальных комнат серверов для фильтра (пагинация, поиск)",
    operation_id="getAllServerRoomsFilter",
    tags=["filters"],
)
async def get_all_server_rooms(
    server_service: Annotated[ServerService, Depends(get_server_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по комнате")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных комнат, в которых зарегистрированы серверы.

    - **200** — список комнат (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await server_service.get_all_rooms_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


# Получение по ID


@router.get(
    "/{server_id}",
    response_model=ServerRead,
    summary="Сервер по ID",
    operation_id="getServerById",
)
async def get_server_by_id(
    server_id: Annotated[int, Path(ge=1, description="ID сервера")],
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerRead:
    """
    Возвращает сервер по ID без загрузки связей.
    Для данных с подразделением и VLAN-ами использовать GET /servers/{server_id}/full.

    - **200** — сервер найден
    - **404** — сервер с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await server_service.get_by_id(server_id=server_id)  # type: ignore[return-value]


@router.get(
    "/{server_id}/full",
    response_model=ServerFullRead,
    summary="Сервер по ID с подразделением и VLAN-ами",
    operation_id="getServerByIdFull",
)
async def get_server_by_id_full(
    server_id: Annotated[int, Path(ge=1, description="ID сервера")],
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerFullRead:
    """
    Возвращает сервер по ID с загруженным подразделением и его VLAN-ами.

    - **200** — сервер найден
    - **404** — сервер с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await server_service.get_by_id_with_relations(server_id=server_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=ServerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать сервер",
    operation_id="createServer",
)
async def create_server(
    server: ServerCreate,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerRead:
    """
    Создаёт новый сервер.

    - **201** — сервер создан, возвращает объект с присвоенным `id`
    - **400** — подразделение с указанным `division_id` не существует; или пользователь с указанным `admin_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await server_service.create(server=server)  # type: ignore[return-value]


@router.patch(
    "/{server_id}",
    response_model=ServerRead,
    summary="Обновить сервер",
    operation_id="updateServer",
)
async def update_server(
    server_id: Annotated[int, Path(ge=1, description="ID сервера")],
    server: ServerUpdate,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerRead:
    """
    Обновляет поля сервера по ID. Передавать только те поля, которые нужно изменить.

    - **200** — сервер обновлён
    - **400** — подразделение с указанным `division_id` не существует; или пользователь с указанным `admin_id` не существует
    - **404** — сервер с таким ID не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await server_service.update(server_id=server_id, server=server)  # type: ignore[return-value]


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сервер",
    operation_id="deleteServer",
)
async def delete_server(
    server_id: Annotated[int, Path(ge=1, description="ID сервера")],
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> None:
    """
    Удаляет сервер по ID. Тело ответа при успехе отсутствует.

    - **204** — сервер удалён
    - **404** — сервер с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    await server_service.delete(server_id=server_id)
