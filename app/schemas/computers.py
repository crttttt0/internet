from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from .divisions import DivisionRead
from .os import OSRead
from .status_disabled import StatusDisabledRead
from .users import UserRead


class ComputerCreate(BaseModel):
    """Схема для создания нового компьютера (с валидацией длин полей)"""

    mac: Annotated[
        str | None, Field(None, max_length=50, description="MAC-адрес устройства")
    ]
    ip: Annotated[str, Field(description="IP-адрес устройства в виде строки")]
    build: Annotated[
        str | None, Field(None, max_length=255, description="Сборка/билдинг")
    ]
    pc_room: Annotated[
        str | None, Field(None, max_length=255, description="Номер комнаты/кабинета")
    ]
    switch_room: Annotated[
        str | None,
        Field(None, max_length=255, description="Номер комм. шкафа/кроссовой"),
    ]
    name: Annotated[
        str | None, Field(None, max_length=255, description="Сетевое имя компьютера")
    ]
    info: Annotated[
        str | None, Field(None, max_length=500, description="Дополнительная информация")
    ]
    access_1c: Annotated[bool, Field(default=False, description="Доступ к 1С")] = False
    access_glx: Annotated[bool, Field(default=False, description="Доступ к GLX")] = (
        False
    )

    division_id: Annotated[int, Field(description="ID подразделения")]
    user_id: Annotated[int | None, Field(None, description="ID пользователя")]
    os_id: Annotated[int | None, Field(None, description="ID операционной системы")]


class ComputerUpdate(BaseModel):
    """Схема для обновления данных компьютера, все поля опциональны"""

    mac: Annotated[str | None, Field(None, max_length=50)]
    ip: Annotated[str | None, Field(None)]
    build: Annotated[str | None, Field(None, max_length=255)]
    pc_room: Annotated[str | None, Field(None, max_length=255)]
    switch_room: Annotated[str | None, Field(None, max_length=255)]
    name: Annotated[str | None, Field(None, max_length=255)]
    info: Annotated[str | None, Field(None, max_length=500)]
    access_1c: Annotated[bool | None, Field(None)]
    access_glx: Annotated[bool | None, Field(None)]

    division_id: Annotated[int | None, Field(None)]
    user_id: Annotated[int | None, Field(None)]
    os_id: Annotated[int | None, Field(None)]


class ComputerRead(BaseModel):
    """Схема для отдачи базовых данных компьютера клиенту (без джойнов)"""

    id: Annotated[int, Field(description="Уникальный идентификатор компьютера")]
    ip: Annotated[str, Field(description="IP-адрес устройства")]
    mac: Annotated[str | None, Field(description="MAC-адрес устройства")]
    build: Annotated[str | None, Field(description="Сборка/билдинг")]
    pc_room: Annotated[str | None, Field(description="Номер комнаты/кабинета")]
    switch_room: Annotated[str | None, Field(description="Номер комм. шкафа/кроссовой")]
    name: Annotated[str | None, Field(description="Сетевое имя компьютера")]
    date: Annotated[
        datetime, Field(description="Дата и время создания/обновления записи")
    ]
    info: Annotated[str | None, Field(description="Дополнительная информация")]
    access_1c: Annotated[bool, Field(description="Доступ к 1С")]
    access_glx: Annotated[bool, Field(description="Доступ к GLX")]

    division_id: Annotated[int, Field(description="ID подразделения")]
    user_id: Annotated[int | None, Field(None, description="ID пользователя")]
    os_id: Annotated[int | None, Field(None, description="ID операционной системы")]

    model_config = ConfigDict(from_attributes=True)


class ComputerFullRead(ComputerRead):
    """Схема для отдачи данных компьютера со всеми развёрнутыми связями"""

    division: Annotated[DivisionRead, Field(description="Подразделение")]
    os_info: Annotated[OSRead | None, Field(None, description="Установленная ОС")]
    user: Annotated[UserRead | None, Field(None, description="Пользователь")]
    status_disabled: Annotated[
        StatusDisabledRead | None, Field(None, description="Статус отключения")
    ]


class ComputerFilters(BaseModel):
    """Query-параметры для фильтрации и поиска компьютеров"""

    build: Annotated[str | None, Field(None, description="Корпус")]
    pc_room: Annotated[str | None, Field(None, description="Комната")]
    division_id: Annotated[int | None, Field(None, description="ID отдела")]
    os_id: Annotated[int | None, Field(None, description="ID операционной системы")]
    vlan_name: Annotated[str | None, Field(None, description="Название VLAN")]
    user_id: Annotated[int | None, Field(None, description="ID пользователя")]
    is_disabled: Annotated[bool | None, Field(None, description="Отключён: true/false")]
    search: Annotated[
        str | None,
        Field(None, description="Поиск по имени компьютера (name)"),
    ]
