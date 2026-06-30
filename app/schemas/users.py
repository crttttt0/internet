from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .divisions import DivisionRead


class UserCreate(BaseModel):
    """Схема для создания нового пользователя"""

    first_name: Annotated[
        str, Field(max_length=100, description="Имя пользователя, до 100 символов")
    ]
    last_name: Annotated[
        str, Field(max_length=100, description="Фамилия пользователя, до 100 символов")
    ]
    patronymic: Annotated[
        str | None,
        Field(
            None, max_length=100, description="Отчество пользователя, до 100 символов"
        ),
    ]
    phone: Annotated[
        str, Field(max_length=20, description="Номер телефона, до 20 символов")
    ]
    email: Annotated[
        str | None,
        Field(None, max_length=50, description="Электронная почта, до 50 символов"),
    ]
    domain_login: Annotated[
        str, Field(max_length=100, description="Доменный логин, до 100 символов")
    ]
    division_id: Annotated[int, Field(description="Идентификатор подразделения")]
    domain_password: Annotated[
        str,
        Field(
            max_length=255,
            description="Хеш пароля от доменной учетной записи, до 255 символов",
        ),
    ]


class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя (все поля опциональны)"""

    first_name: Annotated[
        str | None,
        Field(None, max_length=100, description="Имя пользователя, до 100 символов"),
    ]
    last_name: Annotated[
        str | None,
        Field(
            None, max_length=100, description="Фамилия пользователя, до 100 символов"
        ),
    ]
    patronymic: Annotated[
        str | None,
        Field(
            None, max_length=100, description="Отчество пользователя, до 100 символов"
        ),
    ]
    phone: Annotated[
        str | None,
        Field(None, max_length=20, description="Номер телефона, до 20 символов"),
    ]
    email: Annotated[
        str | None,
        Field(None, max_length=50, description="Электронная почта, до 50 символов"),
    ]
    domain_login: Annotated[
        str | None,
        Field(None, max_length=100, description="Доменный логин, до 100 символов"),
    ]
    domain_password: Annotated[
        str | None,
        Field(
            None,
            max_length=255,
            description="Пароль от доменной учетной записи, до 255 символов",
        ),
    ]
    division_id: Annotated[
        int | None, Field(None, description="Идентификатор подразделения")
    ]


class UserRead(BaseModel):
    """Схема для отдачи данных пользователя клиенту"""

    id: Annotated[int, Field(description="Уникальный идентификатор пользователя")]
    first_name: Annotated[str, Field(description="Имя пользователя")]
    last_name: Annotated[str, Field(description="Фамилия пользователя")]
    patronymic: Annotated[str | None, Field(description="Отчество пользователя")]
    phone: Annotated[str, Field(description="Номер телефона")]
    input_date: Annotated[date, Field(description="Дата внесения записи")]
    email: Annotated[str | None, Field(description="Электронная почта")]
    domain_login: Annotated[str, Field(description="Доменный логин")]
    division_id: Annotated[int, Field(description="Идентификатор подразделения")]

    @computed_field(description="Полное ФИО пользователя")
    @property
    def full_name(self) -> str:
        return " ".join(
            filter(None, [self.last_name, self.first_name, self.patronymic])
        )

    model_config = ConfigDict(from_attributes=True)


class UserWithDivisionRead(UserRead):
    """Схема для отдачи данных пользователя вместе с подразделением клиенту"""

    division: Annotated[DivisionRead, Field(description="Подразделение")]


class UserFilters(BaseModel):
    """Query-параметры для фильтрации и поиска пользователей"""

    division_id: Annotated[
        int | None, Field(None, ge=1, description="ID подразделения")
    ]
    email: Annotated[str | None, Field(None, max_length=50, description="Email")]
    phone: Annotated[str | None, Field(None, max_length=20, description="Телефон")]
    input_date_from: Annotated[date | None, Field(None, description="Дата внесения от")]
    input_date_to: Annotated[date | None, Field(None, description="Дата внесения до")]
    search: Annotated[
        str | None, Field(None, max_length=100, description="Поиск по ФИО")
    ]
