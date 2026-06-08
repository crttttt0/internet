from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Division(Base):
    """Подразделения (НТК - Отделение - Отдел)"""

    __tablename__ = "divisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    stc: Mapped[str | None] = mapped_column(String(50))
    branch: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50))
