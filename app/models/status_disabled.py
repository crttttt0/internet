from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import Computer


class StatusDisabled(Base):
    """Причина отключения компьютера (красная строка в списке)"""

    __tablename__ = "status_disabled"

    id: Mapped[int] = mapped_column(primary_key=True)
    computer_id: Mapped[int] = mapped_column(ForeignKey("computers.id"), unique=True)
    reason: Mapped[str | None] = mapped_column(String(500))

    computer: Mapped[Computer] = relationship(
        back_populates="status_disabled", lazy="raise"
    )
