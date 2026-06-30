from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_os_service
from app.schemas.filters import FilterOption
from app.schemas.os import OSCreate, OSRead, OSUpdate
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services import OSService

router = APIRouter(prefix="/os", tags=["os"])


# Получение


@router.get(
    "/",
    response_model=PaginatedResponse[OSRead],
    summary="Список ОС (пагинация, поиск)",
    operation_id="getAllOs",
)
async def get_all_os(
    os_service: Annotated[OSService, Depends(get_os_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по названию ОС")
    ] = None,
) -> PaginatedResponse[OSRead]:
    """
    Возвращает список операционных систем с пагинацией и поиском по названию.

    - **200** — список ОС (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await os_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


# Получение фильтров


@router.get(
    "/filter",
    response_model=PaginatedResponse[FilterOption],
    summary="Список ОС для фильтра (пагинация, поиск)",
    operation_id="getAllOsFilter",
    tags=["filters"],
)
async def get_all_os_filter(
    os_service: Annotated[OSService, Depends(get_os_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по названию ОС")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список операционных систем в формате для селекта.

    - **200** — список ОС (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await os_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=str(item.id), label=item.name) for item in items],
    )


# Получение по ID


@router.get(
    "/{os_id}",
    response_model=OSRead,
    summary="ОС по ID",
    operation_id="getOsById",
)
async def get_os_by_id(
    os_id: Annotated[int, Path(ge=1, description="ID операционной системы")],
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> OSRead:
    """
    Возвращает операционную систему по ID.

    - **200** — ОС найдена
    - **404** — ОС с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await os_service.get_by_id(os_id=os_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=OSRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать ОС",
    operation_id="createOs",
)
async def create_os(
    os: OSCreate,
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> OSRead:
    """
    Создаёт новую операционную систему. Поля name и icon_name должны быть уникальными.

    - **201** — ОС создана, возвращает объект с присвоенным id
    - **422** — ошибка валидации тела запроса
    """

    return await os_service.create(os=os)  # type: ignore[return-value]


@router.patch(
    "/{os_id}",
    response_model=OSRead,
    summary="Обновить ОС по ID",
    operation_id="updateOs",
)
async def update_os(
    os_id: Annotated[int, Path(ge=1, description="ID операционной системы")],
    os: OSUpdate,
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> OSRead:
    """
    Обновляет поля ОС по ID. Передавать только те поля, которые нужно изменить.

    - **200** — ОС обновлена
    - **404** — ОС с таким ID не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await os_service.update(os_id=os_id, os=os)  # type: ignore[return-value]


@router.delete(
    "/{os_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ОС",
    operation_id="deleteOS",
)
async def delete_os(
    os_id: Annotated[int, Path(ge=1, description="ID операционной системы")],
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> None:
    """
    Удаляет ОС по ID. Тело ответа при успехе отсутствует.

    - **204** — ОС удалена
    - **404** — ОС с таким ID не существует
    - **409** — к данной ОС привязаны компьютеры
    - **422** — ID должен быть больше или равен 1
    """

    await os_service.delete(os_id=os_id)
