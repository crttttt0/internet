import ipaddress
from datetime import datetime

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    chief_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    os: Mapped[int | None] = mapped_column(ForeignKey("os.id"))

    @property
    def ip(self) -> str:
        return str(ipaddress.ip_address(self._ip))

    @ip.setter
    def ip(self, value: str):
        self._ip = ipaddress.ip_address(value).packed
