from decimal import Decimal

from sqlalchemy import NUMERIC, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel
from app.database.mixin import DateTimeAtMixin


class User(BaseModel, DateTimeAtMixin):
    """
    Represents a user in the application.

    This class provides a model for storing user-related data in the database,
    including attributes such as user ID, username, preferred language, and
    balance. It extends the BaseModel with functionality for handling creation
    and update timestamps through the DateTimeAtMixin.

    Attributes:
        user_id: An integer representing the unique identifier for the user.
        username: A string or None representing the username of the user.
        language: A 3-letter string denoting the user's preferred language.
            Defaults to 'ru'.
        balance: A Decimal representing the user's account balance. Uses high
            precision with a fixed scale of eight decimal places. Defaults to 0.00.
    """

    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    language: Mapped[str] = mapped_column(
        String(3), default="ru", nullable=False, server_default="ru"
    )
    balance: Mapped[Decimal] = mapped_column(
        NUMERIC(precision=18, scale=8),
        default=Decimal("0.00"),
        nullable=False,
        server_default="0.00",
    )

    def __repr__(self):
        return (
            f"User("
            f"user_id={self.user_id}, "
            f"username={self.username}, "
            f"language={self.language}, "
            f"balance={self.balance}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}"
            f")"
        )
