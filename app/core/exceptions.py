class BaseAppException(Exception):
    """Базовое исключение бизнес-логики приложения"""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class InvalidForeignKeyException(BaseAppException):
    """Переданный FK-идентификатор ссылается на несуществующую запись"""

    pass


class EntityNotFoundException(BaseAppException):
    """Какая-то сущность (юзер, отдел, сессия) не найдена в системе"""

    pass


class EntityAlreadyExistsException(BaseAppException):
    """Попытка создать дубликат уникальных данных (email, login)"""

    pass


class AuthenticationFailedException(BaseAppException):
    """Пользователь ввёл неверный пароль или логин"""

    pass


class AccessDeniedException(BaseAppException):
    """У пользователя недостаточно прав для этого действия"""

    pass


class BusinessRuleViolationException(BaseAppException):
    """Нарушено какое-то внутреннее правило (например, нельзя удалить последнее подразделение)"""

    pass
