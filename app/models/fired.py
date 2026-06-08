from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Fired(Base):
    """Уволенные сотрудники (имена для блокировки)"""

    __tablename__ = "fired"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sname: Mapped[str | None] = mapped_column(String(50))
