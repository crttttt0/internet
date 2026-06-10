from app.core.exceptions import EntityNotFoundException
from app.models import User
from app.repositories import UserRepository
from app.schemas.users import UserCreate
from app.services import DivisionService


class UserService:
    def __init__(
        self, user_repository: UserRepository, division_service: DivisionService
    ) -> None:
        self.user_repository = user_repository
        self.division_service = division_service

    async def get_by_id(self, user_id: int) -> User:
        db_user = await self.user_repository.get_by_id_with_division(user_id)
        if not db_user:
            raise EntityNotFoundException(f"Пользователь с ID {user_id} не найден")

        return db_user

    async def create(self, user: UserCreate) -> User:
        await self.division_service.get_by_id(user.division_id)
        db_user = await self.user_repository.create(**user.model_dump())
        return db_user
