import datetime
import ipaddress

from sqlalchemy import ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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

    @property
    def ip(self) -> str:
        return str(ipaddress.ip_address(self._ip))

    @ip.setter
    def ip(self, value: str):
        self._ip = ipaddress.ip_address(value).packed
