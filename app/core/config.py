from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration and settings management for the application.

    This class inherits from `BaseSettings` to provide environment-based configuration
    and centralized management for application-related settings. It encapsulates
    database configurations, application tokens, webhook paths, logging levels,
    and other settings required for running the application. These configurations
    are typically loaded from environment variables or default values.

    Attributes:
        PUBLIC_URL (str | None): The publicly accessible URL for the application.
            Useful for webhook registration and external integrations.
        BOT_TOKEN (str): Token used for authenticating the bot with the Telegram API.
        TELEGRAM_WEBHOOK_PATH (str | None): Path for the Telegram bot webhook endpoint.
        TELEGRAM_WEBHOOK_SECRET_TOKEN (str | None): Secret token for validating
            incoming webhook requests from Telegram.
        TELEGRAM_WEBHOOK_IP_ADDRESS (str | None): Optional IP address for Telegram webhook binding.

        POSTGRES_HOST (str): Hostname of the PostgreSQL server.
        POSTGRES_PORT (int): Port number of the PostgreSQL server.
        POSTGRES_USER (str): Username for connecting to the PostgreSQL database.
        POSTGRES_PASSWORD (str): Password for the PostgreSQL user.
        POSTGRES_DB (str): Name of the PostgreSQL database to connect to.

        REDIS_HOST (str): Hostname of the Redis server.
        REDIS_PORT (int): Port number of the Redis server.
        REDIS_PASSWORD (str): Password for connecting to the Redis instance.
        REDIS_DB (int): Redis database number to use.

        LOG_LEVEL (str): Log level for application logging (e.g., "DEBUG", "INFO").
        LOG_FORMAT (Literal["plain", "json"]): Format in which logs should be output.

        NGROK_AUTHTOKEN (str | None): Authentication token for the Ngrok service,
            used for creating tunnels to local webhook endpoints.

        PAYMENT_WEBHOOK_PATH (str | None): Path for the payment service webhook endpoint.
        CRYPTOBOT_TOKEN (str | None): Token for integrating with the Cryptobot payment service.

        ADMIN_CHAT_ID (int | None): Telegram chat ID for administrative notifications.
        BACKUP_CHAT_ID (int | None): Telegram chat ID for receiving backup data.
    """

    PUBLIC_URL: str | None = None

    BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_PATH: str | None = "/webhook/bot"
    TELEGRAM_WEBHOOK_SECRET_TOKEN: str | None = None
    TELEGRAM_WEBHOOK_IP_ADDRESS: str | None = None

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "postgres"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "redis_password"
    REDIS_DB: int = 0
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["plain", "json"] = "plain"

    NGROK_AUTHTOKEN: str | None = None

    PAYMENT_WEBHOOK_PATH: str | None = "/webhook/payment"
    CRYPTOBOT_TOKEN: str | None = None

    ADMIN_CHAT_ID: int | None = None

    BACKUP_CHAT_ID: int | None = None

    WEB_APP_PATH: str | None = "/api/webapp"

    @property
    def POSTGRES_URI(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
