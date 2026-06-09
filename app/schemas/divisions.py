from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DivisionCreate(BaseModel):
    """Схема для создания нового подразделения"""

    stc: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Научно-технический комплекс (НТК), до 50 символов",
        ),
    ]
    branch: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Отделение подразделения, до 50 символов",
        ),
    ]
    department: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Конкретный отдел, до 50 символов",
        ),
    ]


class DivisionUpdate(BaseModel):
    """Схема для обновления данных подразделения (все поля опциональны)"""

    stc: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Научно-технический комплекс (НТК), до 50 символов",
        ),
    ]
    branch: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Отделение подразделения, до 50 символов",
        ),
    ]
    department: Annotated[
        str | None,
        Field(
            None,
            max_length=50,
            description="Конкретный отдел, до 50 символов",
        ),
    ]


class DivisionRead(BaseModel):
    """Схема для отдачи данных подразделения клиенту (без валидации ограничений)"""

    id: Annotated[int, Field(description="Уникальный идентификатор подразделения")]
    stc: Annotated[str | None, Field(description="Научно-технический комплекс (НТК)")]
    branch: Annotated[str | None, Field(description="Отделение подразделения")]
    department: Annotated[str | None, Field(description="Конкретный отдел")]

    model_config = ConfigDict(from_attributes=True)
