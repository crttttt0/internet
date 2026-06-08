from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OS(Base):
    """Справочник типов устройств, ОС"""

    __tablename__ = "os"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    icon_name: Mapped[str] = mapped_column(String(255), unique=True)
