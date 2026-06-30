from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class OSCreate(BaseModel):
    """Схема для создания новой ОС"""

    name: Annotated[
        str,
        Field(
            max_length=50, description="Название операционной системы, до 50 символов"
        ),
    ]
    icon_name: Annotated[
        str,
        Field(
            max_length=255, description="Имя иконки для отображения, до 255 символов"
        ),
    ]


class OSUpdate(BaseModel):
    """Схема для обновления данных ОС, все поля опциональны"""

    name: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Название операционной системы, до 50 символов",
        ),
    ]
    icon_name: Annotated[
        str | None,
        Field(
            None,
            max_length=255,
            description="Имя иконки для отображения, до 255 символов",
        ),
    ]


class OSRead(BaseModel):
    """Схема для отдачи данных операционной системы клиенту"""

    id: Annotated[int, Field(description="Уникальный идентификатор ОС")]
    name: Annotated[str, Field(description="Название операционной системы")]
    icon_name: Annotated[str, Field(description="Имя иконки для отображения")]

    model_config = ConfigDict(from_attributes=True)
