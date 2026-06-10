from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import Computer


class OS(Base):
    """Справочник типов устройств, ОС"""

    __tablename__ = "os"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    icon_name: Mapped[str] = mapped_column(String(255), unique=True)

    computers: Mapped[list[Computer]] = relationship(
        back_populates="os_info", lazy="raise"
    )
