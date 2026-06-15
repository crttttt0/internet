from __future__ import annotations

import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .divisions import DivisionRead
from .vlans import VlanRead


class ServerCreate(BaseModel):
    """Схема для создания нового сервера (с валидацией длин полей)"""

    ip: Annotated[str, Field(description="IP-адрес сервера в виде строки")]
    mac: Annotated[
        str | None, Field(None, max_length=50, description="MAC-адрес сервера")
    ]
    room: Annotated[
        str | None, Field(None, max_length=50, description="Номер комнаты/кабинета")
    ]
    build: Annotated[str | None, Field(None, max_length=50, description="Корпус")]

    division_id: Annotated[int | None, Field(None, description="ID подразделения")]
    admin_id: Annotated[
        int | None, Field(None, description="ID администратора (пользователя)")
    ]


class ServerUpdate(BaseModel):
    """Схема для обновления данных сервера, все поля опциональны"""

    ip: Annotated[str | None, Field(None, description="IP-адрес сервера в виде строки")]
    mac: Annotated[str | None, Field(None, max_length=50)]
    room: Annotated[str | None, Field(None, max_length=50)]
    build: Annotated[str | None, Field(None, max_length=50)]

    division_id: Annotated[int | None, Field(None)]
    admin_id: Annotated[int | None, Field(None)]


class ServerRead(BaseModel):
    """Схема для отдачи базовых данных сервера клиенту (без джойнов)"""

    id: Annotated[int, Field(description="Уникальный идентификатор сервера")]
    ip: Annotated[str, Field(description="IP-адрес сервера")]
    mac: Annotated[str | None, Field(description="MAC-адрес сервера")]
    room: Annotated[str | None, Field(description="Номер комнаты/кабинета")]
    build: Annotated[str | None, Field(description="Корпус")]
    date: Annotated[datetime.date, Field(description="Дата добавления записи")]

    division_id: Annotated[int | None, Field(description="ID подразделения")]
    admin_id: Annotated[int | None, Field(description="ID администратора")]

    model_config = ConfigDict(from_attributes=True)


class ServerFullRead(ServerRead):
    """Схема для отдачи данных сервера с развёрнутым подразделением и его VLAN-ами"""

    division: Annotated[DivisionRead | None, Field(description="Подразделение")]
    vlans: Annotated[list[VlanRead], Field(description="VLAN-ы подразделения сервера")]

    @model_validator(mode="before")
    @classmethod
    def extract_vlans_from_division(cls, data: object) -> object:
        """Вытащить VLAN-ы из division.vlans, если division загружен"""

        if hasattr(data, "division") and data.division is not None:
            try:
                data.__dict__["vlans"] = data.division.vlans
            except Exception:
                data.__dict__.setdefault("vlans", [])
        return data
