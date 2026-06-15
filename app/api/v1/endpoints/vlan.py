from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_vlan_service
from app.schemas.vlans import (
    VlanCreate,
    VlanRead,
    VlanUpdate,
    VlanWithDivisionsRead,
)
from app.services import VlanService

router = APIRouter(prefix="/vlans", tags=["vlans"])


@router.get(
    "/", response_model=list[VlanWithDivisionsRead], summary="Список всех VLAN-ов"
)
async def get_all_vlans(
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Максимальное количество записей в ответе"),
    ] = 24,
) -> Sequence[VlanWithDivisionsRead]:
    """
    Возвращает список всех VLAN-ов с привязанными подразделениями и пагинацией.

    - **200** — список VLAN-ов (может быть пустым)
    """

    return await vlan_service.get_all_with_divisions(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/{vlan_id}", response_model=VlanRead, summary="VLAN по ID")
async def get_vlan_by_id(
    vlan_id: int,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanRead:
    """
    Возвращает VLAN по ID без подразделений.
    Если нужны подразделения — использовать `GET /vlans/{vlan_id}/divisions`

    - **200** — VLAN найден
    - **404** — VLAN с таким ID не существует
    """

    return await vlan_service.get_by_id(vlan_id)  # type: ignore[return-value]


@router.get(
    "/{vlan_id}/divisions",
    response_model=VlanWithDivisionsRead,
    summary="VLAN по ID вместе с подразделениями",
)
async def get_vlan_with_divisions_by_id(
    vlan_id: int,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanWithDivisionsRead:
    """
    Возвращает VLAN по ID вместе со списком привязанных подразделений.
    Если подразделений нет, поле `divisions` будет пустым массивом

    - **200** — VLAN найден
    - **404** — VLAN с таким ID не существует
    """

    return await vlan_service.get_by_id_with_divisions(vlan_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=VlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать VLAN",
)
async def create_vlan(
    vlan: VlanCreate,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanRead:
    """
    Создает новый VLAN.

    - **201** — VLAN создан, возвращает объект с присвоенным `id`
    - **422** — ошибка валидации тела запроса (например, превышена длина поля)
    """

    return await vlan_service.create(vlan)  # type: ignore[return-value]


@router.patch("/{vlan_id}", response_model=VlanRead, summary="Обновить VLAN")
async def update_vlan(
    vlan_id: int,
    vlan: VlanUpdate,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanRead:
    """
    Обновляет поля VLAN-а по ID. Передавать только те поля, которые нужно изменить.

    - **200** — VLAN обновлен
    - **404** — VLAN с таким ID не существует
    - **422** — ошибка валидации тела запроса
    """

    return await vlan_service.update(vlan_id, vlan)  # type: ignore[return-value]


@router.delete(
    "/{vlan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить VLAN",
)
async def delete_vlan(
    vlan_id: int,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> None:
    """
    Удаляет VLAN по ID. Тело ответа при успехе отсутствует.

    - **204** — VLAN удален
    - **404** — VLAN с таким ID не существует
    """

    await vlan_service.delete(vlan_id)
