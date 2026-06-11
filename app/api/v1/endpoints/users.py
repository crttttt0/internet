from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_user_service
from app.schemas.users import UserCreate, UserRead, UserUpdate, UserWithDivisionRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/", response_model=list[UserWithDivisionRead], summary="Список всех пользователей"
)
async def get_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: Annotated[int, Query(ge=0, description="Сколько записей пропустить")] = 0,
    limit: Annotated[
        int,
        Query(ge=1, le=1000, description="Максимальное количество записей в ответе"),
    ] = 24,
) -> Sequence[UserWithDivisionRead]:
    """
    Возвращает список всех пользователей с подразделениями и пагинацией.

    - **200** — список пользователей (может быть пустым)
    """

    return await user_service.get_all_with_division(skip=skip, limit=limit)  # type: ignore[return-value]


@router.get("/{user_id}", response_model=UserRead, summary="Пользователь по ID")
async def get_user_by_id(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Возвращает пользователя по ID без вложенных объектов.
    Если нужно подразделение — использовать `GET /users/{user_id}/division`

    - **200** — пользователь найден
    - **404** — пользователь с таким ID не существует
    """

    return await user_service.get_by_id(user_id=user_id)  # type: ignore[return-value]


@router.get(
    "/{user_id}/division",
    response_model=UserWithDivisionRead,
    summary="Пользователь по ID вместе с подразделением",
)
async def get_user_with_division_by_id(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserWithDivisionRead:
    """
    Возвращает пользователя по ID вместе с подразделением.
    Если подразделение не нужно — использовать `GET /users/{user_id}`

    - **200** — пользователь найден
    - **404** — пользователь с таким ID не существует
    """

    return await user_service.get_by_id_with_division(user_id=user_id)  # type: ignore[return-value]


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
)
async def create_user(
    user: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Создает нового пользователя. Пароль хешируется автоматически перед сохранением.

    - **201** — пользователь создан, возвращает объект с присвоенным `id`
    - **404** — подразделение с указанным `division_id` не существует
    - **422** — ошибка валидации тела запроса (например, превышена длина поля)
    """

    return await user_service.create(user=user)  # type: ignore[return-value]


@router.patch("/{user_id}", response_model=UserRead, summary="Обновить пользователя")
async def update_user(
    user_id: int,
    user: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Обновляет поля пользователя по ID. Передавать только те поля, которые нужно изменить.
    Если передается новый пароль — он будет захеширован автоматически.

    - **200** — пользователь обновлен
    - **404** — пользователь или указанное подразделение не существует
    - **422** — ошибка валидации тела запроса
    """

    return await user_service.update(user_id=user_id, user=user)  # type: ignore[return-value]


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
)
async def delete_user(
    user_id: int,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """
    Удаляет пользователя по ID. Тело ответа при успехе отсутствует.

    - **204** — пользователь удален
    - **404** — пользователь с таким ID не существует
    """

    await user_service.delete(user_id=user_id)
