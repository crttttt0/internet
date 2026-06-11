from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_status_disabled_service
from app.schemas.status_disabled import (
    StatusDisabledCreate,
    StatusDisabledRead,
    StatusDisabledUpdate,
)
from app.services import StatusDisabledService

router = APIRouter(prefix="/status-disabled", tags=["status-disabled"])


@router.get(
    "/computers/{computer_id}",
    response_model=StatusDisabledRead,
    summary="Статус отключения по ID компьютера",
)
async def get_status_by_computer_id(
    computer_id: int,
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> StatusDisabledRead:
    """
    Возвращает статус отключения для указанного компьютера.

    - **200** — статус найден
    - **404** — статус отключения для этого компьютера не существует
    """

    return await status_disabled_service.get_by_computer_id(computer_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=StatusDisabledRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать статус отключения",
)
async def create_status(
    status_disabled: StatusDisabledCreate,
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> StatusDisabledRead:
    """
    Создает статус отключения для компьютера. У одного компьютера может быть только один статус.

    - **201** — статус создан, возвращает объект с присвоенным `id`
    - **409** — статус отключения для этого компьютера уже существует
    - **422** — ошибка валидации тела запроса
    """

    return await status_disabled_service.create(status_disabled)  # type: ignore[return-value]


@router.patch(
    "/computers/{computer_id}",
    response_model=StatusDisabledRead,
    summary="Обновить статус отключения",
)
async def update_status(
    computer_id: int,
    status_disabled: StatusDisabledUpdate,
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> StatusDisabledRead:
    """
    Обновляет поля статуса отключения по ID компьютера. Передавать только те поля, которые нужно изменить.

    - **200** — статус обновлен
    - **404** — статус отключения для этого компьютера не существует
    - **422** — ошибка валидации тела запроса
    """

    return await status_disabled_service.update(computer_id, status_disabled)  # type: ignore[return-value]


@router.delete(
    "/computers/{computer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить статус отключения",
)
async def delete_status(
    computer_id: int,
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> None:
    """
    Удаляет статус отключения по ID компьютера. Тело ответа при успехе отсутствует.

    - **204** — статус удален
    - **404** — статус отключения для этого компьютера не существует
    """

    await status_disabled_service.delete(computer_id)
