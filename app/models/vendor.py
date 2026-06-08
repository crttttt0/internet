from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Vendor(Base):
    """MAC OUI производитель"""

    __tablename__ = "vendors"

    mac: Mapped[str] = mapped_column(String(50), primary_key=True)
    vendor: Mapped[str] = mapped_column(String(250))
