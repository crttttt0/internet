from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_user_service
from app.schemas.users import UserCreate, UserRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int, user_service: Annotated[UserService, Depends(get_user_service)]
) -> UserRead:
    """Получение пользователя по его ID вместе с подразделением"""
    return await user_service.get_by_id(user_id)  # type: ignore[return-value]


@router.post("/{id}", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def get_by_id1(
    user: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserRead:
    """Создание пользователя"""
    return await user_service.create(user)  # type: ignore[return-value]
