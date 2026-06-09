from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import Division


class User(Base):
    """Сотрудники организации"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    patronymic: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    input_date: Mapped[date] = mapped_column(default=date.today)
    email: Mapped[str] = mapped_column(String(50))
    domain_login: Mapped[str] = mapped_column(String(100))
    domain_password: Mapped[str] = mapped_column(String(255))

    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"))

    division: Mapped[Division] = relationship(lazy="raise", back_populates="users")
