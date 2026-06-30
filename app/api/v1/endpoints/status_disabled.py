from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.core.dependencies import get_status_disabled_service
from app.schemas.status_disabled import (
    StatusDisabledCreate,
    StatusDisabledRead,
    StatusDisabledUpdate,
)
from app.services import StatusDisabledService

router = APIRouter(prefix="/status-disabled", tags=["status-disabled"])


# Получение по ID


@router.get(
    "/computers/{computer_id}",
    response_model=StatusDisabledRead,
    summary="Статус отключения по ID компьютера",
    operation_id="getStatusByComputerId",
)
async def get_status_by_computer_id(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> StatusDisabledRead:
    """
    Возвращает статус отключения для указанного компьютера.

    - **200** — статус найден
    - **404** — статус отключения для этого компьютера не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await status_disabled_service.get_by_computer_id(computer_id=computer_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=StatusDisabledRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать статус отключения",
    operation_id="createStatus",
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
    - **400** — компьютер с указанным `computer_id` не существует
    - **409** — статус отключения для этого компьютера уже существует
    - **422** — ошибка валидации тела запроса
    """

    return await status_disabled_service.create(status=status_disabled)  # type: ignore[return-value]


@router.patch(
    "/computers/{computer_id}",
    response_model=StatusDisabledRead,
    summary="Обновить статус отключения",
    operation_id="updateStatus",
)
async def update_status(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    status_disabled: StatusDisabledUpdate,
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> StatusDisabledRead:
    """
    Обновляет поля статуса отключения по ID компьютера. Передавать только те поля, которые нужно изменить.

    - **200** — статус обновлен
    - **404** — статус отключения для этого компьютера не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await status_disabled_service.update(
        computer_id=computer_id, status=status_disabled
    )  # type: ignore[return-value]


@router.delete(
    "/computers/{computer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить статус отключения",
    operation_id="deleteStatus",
)
async def delete_status(
    computer_id: Annotated[int, Path(ge=1, description="ID компьютера")],
    status_disabled_service: Annotated[
        StatusDisabledService, Depends(get_status_disabled_service)
    ],
) -> None:
    """
    Удаляет статус отключения по ID компьютера. Тело ответа при успехе отсутствует.

    - **204** — статус удален
    - **404** — статус отключения для этого компьютера не существует
    - **422** — ID должен быть больше или равен 1
    """

    await status_disabled_service.delete(computer_id=computer_id)
