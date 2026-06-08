from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vlan(Base):
    """VLAN-ы"""

    __tablename__ = "vlans"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    acl: Mapped[str] = mapped_column(String(255))
