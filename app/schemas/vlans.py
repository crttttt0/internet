from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


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
