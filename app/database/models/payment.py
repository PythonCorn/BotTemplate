from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import BaseModel
from app.infrastructure.payments.providers.core.enums import (
    PaymentAsset,
    PaymentProviderName,
    PaymentStatus,
)


class Payment(BaseModel):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id"),
        index=True,
        nullable=False,
    )

    provider: Mapped[PaymentProviderName] = mapped_column(String(32), nullable=False)

    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)

    asset: Mapped[str] = mapped_column(
        String(16), nullable=False, default=PaymentAsset.USD, server_default=PaymentAsset.USD.value
    )

    status: Mapped[PaymentStatus] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=PaymentStatus.CREATED.value,
        server_default=PaymentStatus.CREATED.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"Payment("
            f"user_id={self.user_id}, "
            f"provider={self.provider}, "
            f"amount={self.amount}, "
            f"asset={self.asset}, "
            f"status={self.status}, "
            f"created_at={self.created_at: %Y-%m-%d %H:%M:%S}, "
            f"paid_at={self.paid_at}"
            f")"
        )
