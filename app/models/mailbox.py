from datetime import datetime

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Mailbox(Base):
    """Почтовые ящики Postfix/Zimbra"""

    __tablename__ = "mailbox"

    username: Mapped[str] = mapped_column(String(255), primary_key=True)
    password: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255))
    maildir: Mapped[str] = mapped_column(String(255))
    quota: Mapped[int] = mapped_column(BigInteger, default=0)
    domain: Mapped[str] = mapped_column(String(255))
    created: Mapped[datetime | None] = mapped_column()
    modified: Mapped[datetime | None] = mapped_column()
    active: Mapped[bool] = mapped_column(default=True)
    crypt_password: Mapped[str] = mapped_column(String(255))
