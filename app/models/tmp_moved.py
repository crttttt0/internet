from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TmpMoved(Base):
    """Временная таблица перемещённых записей."""

    __tablename__ = "tmp_moved"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(250))
