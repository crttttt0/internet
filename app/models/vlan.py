from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import Division


class Vlan(Base):
    """VLAN-ы"""

    __tablename__ = "vlans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    acl: Mapped[str | None] = mapped_column(String(255))

    divisions: Mapped[list[Division]] = relationship(
        secondary="vlandiv", back_populates="vlans", viewonly=True, lazy="raise"
    )
