from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VlanDivision(Base):
    """Привязка VLAN к подразделению"""

    __tablename__ = "vlandiv"

    vlan_id: Mapped[int] = mapped_column(ForeignKey("vlans.id"), primary_key=True)
    division_id: Mapped[int] = mapped_column(
        ForeignKey("divisions.id"), primary_key=True
    )
