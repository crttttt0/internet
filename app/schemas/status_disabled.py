from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class StatusDisabledCreate(BaseModel):
    """Схема для создания статуса отключения компьютера"""

    computer_id: Annotated[
        int, Field(description="ID компьютера, которому назначается статус")
    ]
    reason: Annotated[
        str | None,
        Field(
            None,
            max_length=500,
            description="Причина отключения, до 500 символов",
        ),
    ]


class StatusDisabledUpdate(BaseModel):
    """Схема для обновления статуса отключения, все поля опциональны"""

    reason: Annotated[
        str | None,
        Field(
            None,
            max_length=500,
            description="Причина отключения, до 500 символов",
        ),
    ]


class StatusDisabledRead(BaseModel):
    """Схема для отдачи данных статуса отключения клиенту"""

    id: Annotated[int, Field(description="Уникальный идентификатор статуса")]
    computer_id: Annotated[int, Field(description="ID компьютера")]
    reason: Annotated[str | None, Field(description="Причина отключения")]

    model_config = ConfigDict(from_attributes=True)
