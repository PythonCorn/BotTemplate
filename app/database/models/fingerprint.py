from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import BaseModel

if TYPE_CHECKING:
    from app.database.models.user import User


class Fingerprint(BaseModel):
    """
    Represents a unique fingerprint associated with a user.

    This class is used to store and manage the fingerprint data, which includes
    information about the user's device, browser, and other contextual details.
    It is linked to a specific user through the `user_id` foreign key and provides
    a mechanism to uniquely identify a user across sessions.

    Attributes:
        user_id (int): The ID of the associated user. This is a foreign key field
            that references the `users` table.
        fingerprint_hash (str): A unique hash value of the fingerprint, used for
            identifying the user.
        ip (str | None): The IP address of the user, if provided.
        user_agent (str | None): The user agent string from the user's browser,
            which contains browser and operating system details.
        vendor (str | None): The vendor of the device or browser.
        renderer (str | None): The renderer of the device for graphical output.
        screen_width (int | None): The width of the user's screen in pixels.
        screen_height (int | None): The height of the user's screen in pixels.
        color_depth (int | None): The color depth of the user's screen.
        device_pixel_ratio (float | None): The ratio of the resolution in physical
            pixels to the resolution in logical pixels on the device's screen.
        platform (str | None): The name of the user's operating system or platform.
        device_platform (str | None): The specific platform of the device, indicating
            additional attributes about the system.
        language (str | None): The preferred language of the user's browser or system.
        timezone (str | None): The timezone configured on the user's device.
        created_at (datetime): The datetime when the fingerprint was first created.
        last_seen_at (datetime): The datetime when the fingerprint was last seen or updated.
        user (User): The associated User object, providing access to the user's other
            attributes and relationships.
    """

    __tablename__ = "fingerprints"

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        index=True,
    )

    fingerprint_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    vendor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    renderer: Mapped[str | None] = mapped_column(Text, nullable=True)

    screen_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    screen_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    color_depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    device_pixel_ratio: Mapped[float | None] = mapped_column(nullable=True)

    platform: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_platform: Mapped[str | None] = mapped_column(String(100), nullable=True)

    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="fingerprints",
    )

    def __repr__(self):
        return (
            f"Fingerprint("
            f"user_id={self.user_id}, "
            f"fingerprint_hash={self.fingerprint_hash}, "
            f"ip={self.ip}, "
            f"platform={self.platform}, "
            f"device_platform={self.device_platform}, "
            f"created_at={self.created_at}, "
            f"last_seen_at={self.last_seen_at}"
            f")"
        )
