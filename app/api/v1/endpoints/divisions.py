from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_division_service
from app.schemas.divisions import (
    DivisionCreate,
    DivisionFilters,
    DivisionRead,
    DivisionUpdate,
    DivisionWithVlansRead,
)
from app.schemas.filters import FilterOption
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services import DivisionService

router = APIRouter(prefix="/divisions", tags=["divisions"])


# Получение


@router.get(
    "/",
    response_model=PaginatedResponse[DivisionRead],
    summary="Список подразделений (пагинация, поиск)",
    operation_id="getAllDivisions",
)
async def get_all_divisions(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по НТК, отделению и отделу")
    ] = None,
) -> PaginatedResponse[DivisionRead]:
    """
    Возвращает список подразделений с пагинацией и поиском по НТК, отделению и отделу.
    Связи не загружаются — использовать GET /divisions/full для данных с VLAN-ами.

    - **200** — список подразделений (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await division_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=PaginatedResponse[DivisionWithVlansRead],
    summary="Список подразделений с VLAN-ами (пагинация, поиск, фильтры)",
    operation_id="getAllDivisionsFull",
)
async def get_all_divisions_full(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[DivisionFilters, Depends()],
) -> PaginatedResponse[DivisionWithVlansRead]:
    """
    Возвращает список подразделений с загруженными VLAN-ами.
    Поддерживает фильтрацию по НТК, отделению, отделу и VLAN.

    - **200** — список подразделений (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await division_service.get_all_with_relations_search_filters(
        **pagination.model_dump(), **filters.model_dump()
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


# Получение фильтров


@router.get(
    "/filter",
    response_model=PaginatedResponse[FilterOption],
    summary="Список подразделений для фильтра (пагинация, поиск)",
    operation_id="getAllDivisionsFilter",
    tags=["filters"],
)
async def get_all_divisions_filter(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по НТК, отделению и отделу")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список подразделений в формате для селекта.

    - **200** — список подразделений (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await division_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[
            FilterOption(
                value=str(item.id),
                label=" - ".join(filter(None, [item.stc, item.branch, item.department]))
                or str(item.id),
            )
            for item in items
        ],
    )


@router.get(
    "/stc",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных НТК для фильтра (пагинация, поиск)",
    operation_id="getAllDivisionStcFilter",
    tags=["filters"],
)
async def get_all_division_stc(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по НТК")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных значений НТК из всех подразделений.

    - **200** — список НТК (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await division_service.get_all_stc_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


@router.get(
    "/branches",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных отделений для фильтра (пагинация, поиск)",
    operation_id="getAllDivisionBranchesFilter",
    tags=["filters"],
)
async def get_all_division_branches(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по отделению")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных значений отделений из всех подразделений.

    - **200** — список отделений (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await division_service.get_all_branches_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


@router.get(
    "/departments",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных отделов для фильтра (пагинация, поиск)",
    operation_id="getAllDivisionDepartmentsFilter",
    tags=["filters"],
)
async def get_all_division_departments(
    division_service: Annotated[DivisionService, Depends(get_division_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по отделу")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных значений отделов из всех подразделений.

    - **200** — список отделов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await division_service.get_all_departments_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


# Получение по ID


@router.get(
    "/{division_id}",
    response_model=DivisionRead,
    summary="Подразделение по ID",
    operation_id="getDivisionById",
)
async def get_division_by_id(
    division_id: Annotated[int, Path(ge=1, description="ID подразделения")],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionRead:
    """
    Возвращает подразделение по ID без загрузки VLAN-ов.
    Для данных с VLAN-ами использовать GET /divisions/{division_id}/full.

    - **200** — подразделение найдено
    - **404** — подразделение с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await division_service.get_by_id(division_id=division_id)  # type: ignore[return-value]


@router.get(
    "/{division_id}/full",
    response_model=DivisionWithVlansRead,
    summary="Подразделение по ID с VLAN-ами",
    operation_id="getDivisionByIdFull",
)
async def get_division_by_id_full(
    division_id: Annotated[int, Path(ge=1, description="ID подразделения")],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionWithVlansRead:
    """
    Возвращает подразделение по ID с загруженными VLAN-ами.
    Если VLAN-ов нет, поле vlans будет пустым массивом.

    - **200** — подразделение найдено
    - **404** — подразделение с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await division_service.get_by_id_with_relations(division_id=division_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=DivisionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать подразделение",
    operation_id="createDivision",
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

    return await division_service.create(division=division)  # type: ignore[return-value]


@router.patch(
    "/{division_id}",
    response_model=DivisionRead,
    summary="Обновить подразделение",
    operation_id="updateDivision",
)
async def update_division(
    division_id: Annotated[int, Path(ge=1, description="ID подразделения")],
    division: DivisionUpdate,
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> DivisionRead:
    """
    Обновляет поля подразделения по ID. Передавать только те поля, которые нужно изменить.

    - **200** — подразделение обновлено
    - **404** — подразделение с таким ID не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await division_service.update(division_id=division_id, division=division)  # type: ignore[return-value]


@router.delete(
    "/{division_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить подразделение",
    operation_id="deleteDivision",
)
async def delete_division(
    division_id: Annotated[int, Path(ge=1, description="ID подразделения")],
    division_service: Annotated[DivisionService, Depends(get_division_service)],
) -> None:
    """
    Удаляет подразделение по ID. Тело ответа при успехе отсутствует.

    - **204** — подразделение удалено
    - **404** — подразделение с таким ID не существует
    - **409** — к подразделению привязаны пользователи или компьютеры
    - **422** — ID должен быть больше или равен 1
    """

    await division_service.delete(division_id=division_id)
