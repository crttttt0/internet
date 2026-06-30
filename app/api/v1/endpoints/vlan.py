from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_vlan_service
from app.schemas.filters import FilterOption
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.vlans import (
    VlanCreate,
    VlanFilters,
    VlanRead,
    VlanUpdate,
    VlanWithDivisionsRead,
)
from app.services import VlanService

router = APIRouter(prefix="/vlans", tags=["vlans"])


# Получение


@router.get(
    "/",
    response_model=PaginatedResponse[VlanRead],
    summary="Список VLAN-ов (пагинация, поиск)",
    operation_id="getAllVlans",
)
async def get_all_vlans(
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=255, description="Поиск по названию и ACL")
    ] = None,
) -> PaginatedResponse[VlanRead]:
    """
    Возвращает список VLAN-ов с пагинацией и поиском по названию и ACL.
    Связи не загружаются — использовать GET /vlans/full для данных с подразделениями.

    - **200** — список VLAN-ов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await vlan_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=PaginatedResponse[VlanWithDivisionsRead],
    summary="Список VLAN-ов с подразделениями (пагинация, поиск, фильтры)",
    operation_id="getAllVlansFull",
)
async def get_all_vlans_full(
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[VlanFilters, Depends()],
) -> PaginatedResponse[VlanWithDivisionsRead]:
    """
    Возвращает список VLAN-ов с загруженными подразделениями.
    Поддерживает фильтрацию по ACL и подразделению.

    - **200** — список VLAN-ов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await vlan_service.get_all_with_relations_search_filters(
        **pagination.model_dump(), **filters.model_dump()
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


# Получение фильтров


@router.get(
    "/filter",
    response_model=PaginatedResponse[FilterOption],
    summary="Список VLAN-ов для фильтра (пагинация, поиск)",
    operation_id="getAllVlansFilter",
    tags=["filters"],
)
async def get_all_vlans_filter(
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=255, description="Поиск по названию и ACL")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список VLAN-ов в формате для селекта.

    - **200** — список VLAN-ов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await vlan_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=str(item.id), label=item.name) for item in items],
    )


@router.get(
    "/acl",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных ACL для фильтра (пагинация, поиск)",
    operation_id="getAllVlanAclFilter",
    tags=["filters"],
)
async def get_all_vlan_acl(
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=255, description="Поиск по ACL")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных значений ACL из всех VLAN-ов.

    - **200** — список ACL (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await vlan_service.get_all_acl_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


# Получение по ID


@router.get(
    "/{vlan_id}",
    response_model=VlanRead,
    summary="VLAN по ID",
    operation_id="getVlanById",
)
async def get_vlan_by_id(
    vlan_id: Annotated[int, Path(ge=1, description="ID VLAN-а")],
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanRead:
    """
    Возвращает VLAN по ID без загрузки подразделений.
    Для данных с подразделениями использовать GET /vlans/{vlan_id}/full.

    - **200** — VLAN найден
    - **404** — VLAN с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await vlan_service.get_by_id(vlan_id=vlan_id)  # type: ignore[return-value]


@router.get(
    "/{vlan_id}/full",
    response_model=VlanWithDivisionsRead,
    summary="VLAN по ID с подразделениями",
    operation_id="getVlanByIdFull",
)
async def get_vlan_by_id_full(
    vlan_id: Annotated[int, Path(ge=1, description="ID VLAN-а")],
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanWithDivisionsRead:
    """
    Возвращает VLAN по ID с загруженными подразделениями.
    Если подразделений нет, поле divisions будет пустым массивом.

    - **200** — VLAN найден
    - **404** — VLAN с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await vlan_service.get_by_id_with_relations(vlan_id=vlan_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=VlanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать VLAN",
    operation_id="createVlan",
)
async def create_vlan(
    vlan: VlanCreate,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanRead:
    """
    Создаёт новый VLAN.

    - **201** — VLAN создан, возвращает объект с присвоенным id
    - **422** — ошибка валидации тела запроса
    """

    return await vlan_service.create(vlan=vlan)  # type: ignore[return-value]


@router.patch(
    "/{vlan_id}",
    response_model=VlanRead,
    summary="Обновить VLAN по ID",
    operation_id="updateVlan",
)
async def update_vlan(
    vlan_id: Annotated[int, Path(ge=1, description="ID VLAN-а")],
    vlan: VlanUpdate,
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> VlanRead:
    """
    Обновляет поля VLAN-а по ID. Передавать только те поля, которые нужно изменить.

    - **200** — VLAN обновлён
    - **404** — VLAN с таким ID не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await vlan_service.update(vlan_id=vlan_id, vlan=vlan)  # type: ignore[return-value]


@router.delete(
    "/{vlan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить VLAN по ID",
    operation_id="deleteVlan",
)
async def delete_vlan(
    vlan_id: Annotated[int, Path(ge=1, description="ID VLAN-а")],
    vlan_service: Annotated[VlanService, Depends(get_vlan_service)],
) -> None:
    """
    Удаляет VLAN по ID. Тело ответа при успехе отсутствует.

    - **204** — VLAN удалён
    - **404** — VLAN с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    await vlan_service.delete(vlan_id=vlan_id)
