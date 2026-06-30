from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .vlans import VlanRead


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
    """Схема для обновления данных подразделения, все поля опциональны)"""

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
    """Схема для отдачи данных подразделения клиенту"""

    id: Annotated[int, Field(description="Уникальный идентификатор подразделения")]
    stc: Annotated[str | None, Field(description="Научно-технический комплекс (НТК)")]
    branch: Annotated[str | None, Field(description="Отделение подразделения")]
    department: Annotated[str | None, Field(description="Конкретный отдел")]

    @computed_field(description="Полное название подразделения")
    @property
    def division_name(self) -> str | None:
        return (
            " - ".join(filter(None, [self.stc, self.branch, self.department])) or None
        )

    model_config = ConfigDict(from_attributes=True)


class DivisionWithVlansRead(DivisionRead):
    """Схема для отдачи данных подразделения вместе с VLAN-ами клиенту"""

    vlans: Annotated[list[VlanRead], Field(description="VLAN-ы подразделения")]


class DivisionFilters(BaseModel):
    """Query-параметры для фильтрации и поиска подразделений"""

    stc: Annotated[str | None, Field(None, max_length=50, description="НТК")]
    branch: Annotated[str | None, Field(None, max_length=50, description="Отделение")]
    department: Annotated[str | None, Field(None, max_length=50, description="Отдел")]
    vlan_id: Annotated[int | None, Field(None, ge=1, description="ID VLAN")]
    search: Annotated[
        str | None,
        Field(None, max_length=50, description="Поиск по НТК, отделению и отделу"),
    ]
