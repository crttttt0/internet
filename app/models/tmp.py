from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Tmp(Base):
    """Временная таблица для импорта компьютеров"""

    __tablename__ = "tmp"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip: Mapped[str | None] = mapped_column(String(50))
    mac: Mapped[str | None] = mapped_column(String(50))
    user: Mapped[str | None] = mapped_column(String(150))
    id_div: Mapped[int | None] = mapped_column()
    build: Mapped[str | None] = mapped_column(String(50))
    room: Mapped[str | None] = mapped_column(String(50))
    room_switch: Mapped[str | None] = mapped_column(String(50))
    admin: Mapped[str | None] = mapped_column(String(150))
    chief: Mapped[str | None] = mapped_column(String(150))
    os: Mapped[str | None] = mapped_column(String(50))
    name: Mapped[str | None] = mapped_column(String(50))
