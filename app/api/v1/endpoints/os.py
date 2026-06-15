from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_os_service
from app.schemas.os import OSCreate, OSRead, OSUpdate
from app.services import OSService

router = APIRouter(prefix="/os", tags=["os"])


@router.get("/", response_model=list[OSRead], summary="Список всех операционных систем")
async def get_all_os(
    os_service: Annotated[OSService, Depends(get_os_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Максимальное количество записей в ответе"),
    ] = 24,
) -> Sequence[OSRead]:
    """
    Возвращает список всех операционных систем с пагинацией.

    - **200** — список ОС (может быть пустым)
    """

    return await os_service.get_all(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/{os_id}", response_model=OSRead, summary="Операционная система по ID")
async def get_os_by_id(
    os_id: int,
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> OSRead:
    """
    Возвращает операционную систему по ID.

    - **200** — ОС найдена
    - **404** — ОС с таким ID не существует
    """

    return await os_service.get_by_id(os_id=os_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=OSRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать операционную систему",
)
async def create_os(
    os: OSCreate,
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> OSRead:
    """
    Создает новую операционную систему.

    - **201** — ОС создана, возвращает объект с присвоенным `id`
    - **422** — ошибка валидации тела запроса (например, превышена длина поля)
    """

    return await os_service.create(os=os)  # type: ignore[return-value]


@router.patch(
    "/{os_id}", response_model=OSRead, summary="Обновить операционную систему"
)
async def update_os(
    os_id: int,
    os: OSUpdate,
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> OSRead:
    """
    Обновляет поля операционной системы по ID. Передавать только те поля, которые нужно изменить.

    - **200** — ОС обновлена
    - **404** — ОС с таким ID не существует
    - **422** — ошибка валидации тела запроса
    """

    return await os_service.update(os_id=os_id, os=os)  # type: ignore[return-value]


@router.delete(
    "/{os_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить операционную систему",
)
async def delete_os(
    os_id: int,
    os_service: Annotated[OSService, Depends(get_os_service)],
) -> None:
    """
    Удаляет операционную систему по ID. Тело ответа при успехе отсутствует.

    - **204** — ОС удалена
    - **404** — ОС с таким ID не существует
    """

    await os_service.delete(os_id=os_id)
