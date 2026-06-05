import json
import logging
import sys
from datetime import UTC, datetime
from logging import LogRecord
from logging.config import dictConfig
from typing import Any


class JsonFormatter(logging.Formatter):
    """Custom logging formatter for generating JSON-formatted log messages.

    Formats log records into a JSON string containing useful metadata for debugging and
    application monitoring. It provides structured logging that can be easily parsed and
    analyzed in logging systems.

    Attributes:
        default_time_format (str): String specifying the default time format for datetime
            serialization, if required.
        default_msec_format (str): String specifying the format for milliseconds in log
            timestamps for consistent time representation.
    """

    def format(self, record: LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(*, level: str = "INFO", json_logs: bool = False) -> None:
    """
    Configures the logging system for the application. It sets up the format, logging levels, and
    handlers for various loggers used within the application. Depending on the `json_logs` flag, the
    log format is either plain text or JSON.

    Args:
        level (str): The logging level to use. Examples include "DEBUG", "INFO", "WARNING", etc.
        json_logs (bool): Flag indicating whether to use JSON formatter for log messages. Defaults to False.

    """
    formatter_name = "json" if json_logs else "plain"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {
                    "format": ("%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "json": {
                    "()": JsonFormatter,
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": formatter_name,
                },
            },
            "root": {
                "level": level,
                "handlers": ["console"],
            },
            "loggers": {
                "uvicorn": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "aiogram": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False,
                },
                "sqlalchemy.engine": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )
