from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_server_service
from app.schemas.servers import (
    ServerCreate,
    ServerFullRead,
    ServerRead,
    ServerUpdate,
)
from app.services import ServerService

router = APIRouter(prefix="/servers", tags=["servers"])


@router.get("/", response_model=list[ServerRead], summary="Список всех серверов")
async def get_all_servers(
    server_service: Annotated[ServerService, Depends(get_server_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Максимальное количество записей в ответе"),
    ] = 24,
) -> Sequence[ServerRead]:
    """
    Возвращает список всех серверов с пагинацией без джойнов.

    - **200** — список серверов (может быть пустым)
    """

    return await server_service.get_all(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=list[ServerFullRead],
    summary="Список всех серверов с подразделениями и VLAN-ами",
)
async def get_all_servers_with_relations(
    server_service: Annotated[ServerService, Depends(get_server_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Максимальное количество записей")
    ] = 24,
) -> Sequence[ServerFullRead]:
    """
    Возвращает список всех серверов с пагинацией, развёрнутым подразделением и VLAN-ами.

    - **200** — список серверов (может быть пустым)
    """

    return await server_service.get_all_with_relations(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/{server_id}", response_model=ServerRead, summary="Сервер по ID")
async def get_server_by_id(
    server_id: int,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerRead:
    """
    Возвращает сервер по ID без джойнов.

    - **200** — сервер найден
    - **404** — сервер с таким ID не существует
    """

    return await server_service.get_by_id(server_id=server_id)  # type: ignore[return-value]


@router.get(
    "/{server_id}/full",
    response_model=ServerFullRead,
    summary="Сервер по ID с подразделением и VLAN-ами",
)
async def get_server_by_id_with_relations(
    server_id: int,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerFullRead:
    """
    Возвращает сервер по ID с развёрнутым подразделением и его VLAN-ами.

    - **200** — сервер найден
    - **404** — сервер с таким ID не существует
    """

    return await server_service.get_by_id_with_relations(server_id=server_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=ServerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать сервер",
)
async def create_server(
    server: ServerCreate,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerRead:
    """
    Создаёт новый сервер.

    - **201** — сервер создан, возвращает объект с присвоенным `id`
    - **404** — подразделение с указанным `division_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await server_service.create(server=server)  # type: ignore[return-value]


@router.patch("/{server_id}", response_model=ServerRead, summary="Обновить сервер")
async def update_server(
    server_id: int,
    server: ServerUpdate,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> ServerRead:
    """
    Обновляет поля сервера по ID. Передавать только те поля, которые нужно изменить.

    - **200** — сервер обновлён
    - **404** — сервер с таким ID не существует, или подразделение с указанным `division_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await server_service.update(server_id=server_id, server=server)  # type: ignore[return-value]


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить сервер",
)
async def delete_server(
    server_id: int,
    server_service: Annotated[ServerService, Depends(get_server_service)],
) -> None:
    """
    Удаляет сервер по ID. Тело ответа при успехе отсутствует.

    - **204** — сервер удалён
    - **404** — сервер с таким ID не существует
    """

    await server_service.delete(server_id=server_id)
