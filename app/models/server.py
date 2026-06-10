from __future__ import annotations

import datetime
import ipaddress
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import Division, User


class Server(Base):
    """Серверы"""

    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    _ip: Mapped[bytes] = mapped_column("ip", LargeBinary(16))
    mac: Mapped[str | None] = mapped_column(String(50))
    room: Mapped[str | None] = mapped_column(String(50))
    build: Mapped[str | None] = mapped_column(String(50))
    date: Mapped[datetime.date] = mapped_column()

    division_id: Mapped[int | None] = mapped_column(ForeignKey("divisions.id"))
    admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    division: Mapped[Division | None] = relationship(
        back_populates="servers", lazy="raise"
    )
    admin: Mapped[User | None] = relationship(
        back_populates="servers_as_admin", foreign_keys=[admin_id], lazy="raise"
    )

    @property
    def ip(self) -> str:
        return str(ipaddress.ip_address(self._ip))

    @ip.setter
    def ip(self, value: str):
        self._ip = ipaddress.ip_address(value).packed
