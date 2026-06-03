from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel
from app.database.mixin import DateTimeAtMixin


class User(BaseModel, DateTimeAtMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    language: Mapped[str] = mapped_column(
        String(3), default="ru", nullable=False, server_default="ru"
    )

    def __repr__(self):
        return (
            f"User("
            f"user_id={self.user_id}, "
            f"username={self.username}, "
            f"language={self.language}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}"
            f")"
        )
