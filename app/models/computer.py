from __future__ import annotations

import ipaddress
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import OS, Division, StatusDisabled, User


class Computer(Base):
    """Рабочие станции, принтеры, сетевые устройства"""

    __tablename__ = "computers"

    id: Mapped[int] = mapped_column(primary_key=True)
    _ip: Mapped[bytes] = mapped_column("ip", LargeBinary(16))
    mac: Mapped[str | None] = mapped_column(String(50))
    build: Mapped[str | None] = mapped_column(String(255))
    pc_room: Mapped[str | None] = mapped_column(String(255))
    switch_room: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    date: Mapped[datetime] = mapped_column()
    info: Mapped[str | None] = mapped_column(String(500))
    access_1c: Mapped[bool] = mapped_column(default=False)
    access_glx: Mapped[bool] = mapped_column(default=False)

    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    chief_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    os_id: Mapped[int | None] = mapped_column(ForeignKey("os.id"))

    division: Mapped[Division] = relationship(back_populates="computers", lazy="raise")
    user: Mapped[User] = relationship(
        back_populates="computers_as_user", foreign_keys=[user_id], lazy="raise"
    )
    admin: Mapped[User] = relationship(
        back_populates="computers_as_admin", foreign_keys=[admin_id], lazy="raise"
    )
    chief: Mapped[User] = relationship(
        back_populates="computers_as_chief", foreign_keys=[chief_id], lazy="raise"
    )
    os_info: Mapped[OS | None] = relationship(back_populates="computers", lazy="raise")
    status_disabled: Mapped[StatusDisabled | None] = relationship(
        back_populates="computer",
        lazy="raise",
        cascade="all, delete-orphan",
        uselist=False,
    )

    @property
    def ip(self) -> str:
        return str(ipaddress.ip_address(self._ip))

    @ip.setter
    def ip(self, value: str):
        self._ip = ipaddress.ip_address(value).packed
