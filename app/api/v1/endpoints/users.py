from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.dependencies import get_user_service
from app.schemas.filters import FilterOption
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.schemas.users import (
    UserCreate,
    UserFilters,
    UserRead,
    UserUpdate,
    UserWithDivisionRead,
)
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


# Получение


@router.get(
    "/",
    response_model=PaginatedResponse[UserRead],
    summary="Список пользователей (пагинация, поиск)",
    operation_id="getAllUsers",
)
async def get_all_users(
    user_service: Annotated[UserService, Depends(get_user_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=100, description="Поиск по ФИО")
    ] = None,
) -> PaginatedResponse[UserRead]:
    """
    Возвращает список пользователей с пагинацией и поиском по ФИО.
    Связи не загружаются — использовать GET /users/full для данных с подразделением.

    - **200** — список пользователей (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await user_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


@router.get(
    "/full",
    response_model=PaginatedResponse[UserWithDivisionRead],
    summary="Список пользователей с подразделением (пагинация, поиск, фильтры)",
    operation_id="getAllUsersFull",
)
async def get_all_users_full(
    user_service: Annotated[UserService, Depends(get_user_service)],
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[UserFilters, Depends()],
) -> PaginatedResponse[UserWithDivisionRead]:
    """
    Возвращает список пользователей с загруженным подразделением.
    Поддерживает фильтрацию по подразделению, email, телефону и диапазону дат внесения.

    - **200** — список пользователей (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await user_service.get_all_with_relations_search_filters(
        **pagination.model_dump(), **filters.model_dump()
    )
    return PaginatedResponse(**pagination.model_dump(), total=total, items=items)  # type: ignore[return-value]


# Получение фильтров


@router.get(
    "/filter",
    response_model=PaginatedResponse[FilterOption],
    summary="Список пользователей для фильтра (пагинация, поиск)",
    operation_id="getAllUsersFilter",
    tags=["filters"],
)
async def get_all_users_filter(
    user_service: Annotated[UserService, Depends(get_user_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=100, description="Поиск по ФИО")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список пользователей в формате для селекта.

    - **200** — список пользователей (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await user_service.get_all_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[
            FilterOption(
                value=str(item.id),
                label=" ".join(
                    filter(None, [item.last_name, item.first_name, item.patronymic])
                ),
            )
            for item in items
        ],
    )


@router.get(
    "/emails",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных email для фильтра (пагинация, поиск)",
    operation_id="getAllUserEmailsFilter",
    tags=["filters"],
)
async def get_all_user_emails(
    user_service: Annotated[UserService, Depends(get_user_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=50, description="Поиск по email")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных email из всех пользователей.

    - **200** — список email (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await user_service.get_all_emails_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


@router.get(
    "/phones",
    response_model=PaginatedResponse[FilterOption],
    summary="Список уникальных телефонов для фильтра (пагинация, поиск)",
    operation_id="getAllUserPhonesFilter",
    tags=["filters"],
)
async def get_all_user_phones(
    user_service: Annotated[UserService, Depends(get_user_service)],
    pagination: Annotated[PaginationParams, Depends()],
    search: Annotated[
        str | None, Query(max_length=20, description="Поиск по телефону")
    ] = None,
) -> PaginatedResponse[FilterOption]:
    """
    Возвращает список уникальных телефонов из всех пользователей.

    - **200** — список телефонов (может быть пустым)
    - **422** — ошибка валидации query-параметров
    """

    items, total = await user_service.get_all_phones_with_search(
        **pagination.model_dump(), search=search
    )
    return PaginatedResponse(
        **pagination.model_dump(),
        total=total,
        items=[FilterOption(value=item, label=item) for item in items],
    )


# Получение по ID


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Пользователь по ID",
    operation_id="getUserById",
)
async def get_user_by_id(
    user_id: Annotated[int, Path(ge=1, description="ID пользователя")],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Возвращает пользователя по ID без загрузки подразделения.
    Для данных с подразделением использовать GET /users/{user_id}/full.

    - **200** — пользователь найден
    - **404** — пользователь с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await user_service.get_by_id(user_id=user_id)  # type: ignore[return-value]


@router.get(
    "/{user_id}/full",
    response_model=UserWithDivisionRead,
    summary="Пользователь по ID с подразделением",
    operation_id="getUserByIdFull",
)
async def get_user_by_id_full(
    user_id: Annotated[int, Path(ge=1, description="ID пользователя")],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserWithDivisionRead:
    """
    Возвращает пользователя по ID с загруженным подразделением.

    - **200** — пользователь найден
    - **404** — пользователь с таким ID не существует
    - **422** — ID должен быть больше или равен 1
    """

    return await user_service.get_by_id_with_relations(user_id=user_id)  # type: ignore[return-value]


# Изменение


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    operation_id="createUser",
)
async def create_user(
    user: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Создаёт нового пользователя.

    - **201** — пользователь создан, возвращает объект с присвоенным `id`
    - **400** — подразделение с указанным `division_id` не существует
    - **422** — ошибка валидации тела запроса
    """

    return await user_service.create(user=user)  # type: ignore[return-value]


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="Обновить пользователя",
    operation_id="updateUser",
)
async def update_user(
    user_id: Annotated[int, Path(ge=1, description="ID пользователя")],
    user: UserUpdate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """
    Обновляет поля пользователя по ID. Передавать только те поля, которые нужно изменить.

    - **200** — пользователь обновлён
    - **400** — подразделение с указанным `division_id` не существует
    - **404** — пользователь с таким ID не существует
    - **422** — ID должен быть больше или равен 1; или ошибка валидации тела запроса
    """

    return await user_service.update(user_id=user_id, user=user)  # type: ignore[return-value]


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    operation_id="deleteUser",
)
async def delete_user(
    user_id: Annotated[int, Path(ge=1, description="ID пользователя")],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """
    Удаляет пользователя по ID. Тело ответа при успехе отсутствует.

    - **204** — пользователь удалён
    - **404** — пользователь с таким ID не существует
    - **422** — к пользователю привязаны компьютеры; или ID должен быть больше или равен 1
    """

    await user_service.delete(user_id=user_id)
