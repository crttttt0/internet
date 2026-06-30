from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .divisions import DivisionRead


class VlanCreate(BaseModel):
    """Схема для создания нового VLAN-а"""

    name: Annotated[
        str,
        Field(
            max_length=255,
            description="Название VLAN-а, до 255 символов",
        ),
    ]
    acl: Annotated[
        str | None,
        Field(
            None,
            max_length=255,
            description="ACL VLAN-а, до 255 символов",
        ),
    ]


class VlanUpdate(BaseModel):
    """Схема для обновления данных VLAN-а (все поля опциональны)"""

    name: Annotated[
        str | None,
        Field(
            None,
            max_length=255,
            description="Название VLAN-а, до 255 символов",
        ),
    ]
    acl: Annotated[
        str | None,
        Field(
            None,
            max_length=255,
            description="ACL VLAN-а, до 255 символов",
        ),
    ]


class VlanRead(BaseModel):
    """Схема для отдачи данных VLAN-а клиенту"""

    id: Annotated[int, Field(description="Уникальный идентификатор VLAN-а")]
    name: Annotated[str, Field(description="Название VLAN-а")]
    acl: Annotated[str | None, Field(description="ACL VLAN-а")]
    model_config = ConfigDict(from_attributes=True)


class VlanWithDivisionsRead(VlanRead):
    """Схема для отдачи данных VLAN-а вместе с подразделениями клиенту"""

    divisions: Annotated[
        list["DivisionRead"], Field(description="Подразделения VLAN-а")
    ]


class VlanFilters(BaseModel):
    """Query-параметры для фильтрации и поиска VLAN-ов"""

    acl: Annotated[str | None, Field(None, max_length=255, description="ACL VLAN-а")]
    division_id: Annotated[
        int | None, Field(None, ge=1, description="ID подразделения")
    ]
    search: Annotated[
        str | None, Field(None, max_length=255, description="Поиск по названию")
    ]
