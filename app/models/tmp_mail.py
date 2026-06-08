from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TmpMail(Base):
    """Временная таблица импорта почтовых ящиков"""

    __tablename__ = "tmp_mail"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip: Mapped[str | None] = mapped_column(String(50))
    mail: Mapped[str | None] = mapped_column(String(150))
    password: Mapped[str | None] = mapped_column(String(50))
    ip1: Mapped[int | None] = mapped_column()
    fio: Mapped[str | None] = mapped_column(String(250))
