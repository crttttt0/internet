from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import Computer, Server, User, Vlan


class Division(Base):
    """Подразделения (НТК - Отделение - Отдел)"""

    __tablename__ = "divisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    stc: Mapped[str | None] = mapped_column(String(50))
    branch: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50))

    users: Mapped[list[User]] = relationship(back_populates="division", lazy="raise")
    computers: Mapped[list[Computer]] = relationship(
        back_populates="division", lazy="raise"
    )
    servers: Mapped[list[Server]] = relationship(
        back_populates="division", lazy="raise"
    )
    vlans: Mapped[list[Vlan]] = relationship(
        secondary="vlandiv", back_populates="divisions", viewonly=True, lazy="raise"
    )
