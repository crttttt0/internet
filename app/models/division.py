from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import User


class Division(Base):
    """Подразделения (НТК - Отделение - Отдел)"""

    __tablename__ = "divisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    stc: Mapped[str | None] = mapped_column(String(50))
    branch: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50))

    users: Mapped[list[User]] = relationship(lazy="raise", back_populates="division")
