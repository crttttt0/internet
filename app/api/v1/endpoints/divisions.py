from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_division_service
from app.schemas.divisions import (
    DivisionCreate,
    DivisionRead,
    DivisionUpdate,
    DivisionWithVlansRead,
)
from app.services import DivisionService

router = APIRouter(prefix="/divisions", tags=["divisions"])


@router.get(
    "/", response_model=list[DivisionWithVlansRead], summary="Список всех подразделений"
)
async def get_all_divisions(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Максимальное количество записей в ответе"),
    ] = 24,
) -> Sequence[DivisionWithVlansRead]:
    """
    Возвращает список всех подразделений с привязанными VLAN-ами и пагинацией.

    - **200** — список подразделений (может быть пустым)
    """

    return await division_service.get_all_with_vlans(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get(
    "/{division_id}", response_model=DivisionRead, summary="Подразделение по ID"
)
async def get_division_by_id(
    division_id: int,
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionRead:
    """
    Возвращает подразделение по ID без VLAN-ов.
    Если нужны VLAN-ы — использовать `GET /divisions/{division_id}/vlans`

    - **200** — подразделение найдено
    - **404** — подразделение с таким ID не существует
    """

    return await division_service.get_by_id(division_id)  # type: ignore[return-value]


@router.get(
    "/{division_id}/vlans",
    response_model=DivisionWithVlansRead,
    summary="Подразделение по ID вместе с VLAN-ами",
)
async def get_division_with_vlans_by_id(
    division_id: int,
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionWithVlansRead:
    """
    Возвращает подразделение по ID вместе со списком привязанных VLAN-ов.
    Если VLAN-ов нет, поле `vlans` будет пустым массивом

    - **200** — подразделение найдено
    - **404** — подразделение с таким ID не существует
    """

    return await division_service.get_by_id_with_vlans(division_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=DivisionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать подразделение",
)
async def create_division(
    division: DivisionCreate,
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionRead:
    """
    Создает новое подразделение. Все поля опциональны, передавать только нужные уровни иерархии.

    - **201** — подразделение создано, возвращает объект с присвоенным `id`
    - **422** — ошибка валидации тела запроса (например, превышена длина поля)
    """

    return await division_service.create(division)  # type: ignore[return-value]


@router.patch(
    "/{division_id}", response_model=DivisionRead, summary="Обновить подразделение"
)
async def update_division(
    division_id: int,
    division: DivisionUpdate,
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionRead:
    """
    Обновляет поля подразделения по ID. Передавать только те поля, которые нужно изменить.

    - **200** — подразделение обновлено
    - **404** — подразделение с таким ID не существует
    - **422** — ошибка валидации тела запроса
    """

    return await division_service.update(division_id, division)  # type: ignore[return-value]


@router.delete(
    "/{division_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить подразделение",
)
async def delete_division(
    division_id: int,
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> None:
    """
    Удаляет подразделение по ID. Тело ответа при успехе отсутствует.

    - **204** — подразделение удалено
    - **404** — подразделение с таким ID не существует
    """

    await division_service.delete(division_id)
