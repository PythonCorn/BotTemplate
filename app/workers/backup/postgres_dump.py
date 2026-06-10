import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("backups")
BACKUP_DIR.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)


async def make_postgres_dump(
    postgres_name: str,
    postgres_host: str,
    postgres_port: int,
    postgres_user: str,
    postgres_password: str,
    extra_name: str | None = None,
) -> Path:
    """
    Creates a PostgreSQL database dump file asynchronously.

    This function generates a dump file for the configured PostgreSQL database
    using the `pg_dump` utility. The dump file is named based on the current
    timestamp and stored in the backup directory. The function ensures proper
    environment configuration for the `pg_dump` command, such as providing the
    database password through an environment variable. If the command fails,
    an error is raised with the details from standard error.

    Raises:
        RuntimeError: If the `pg_dump` command fails, the error message from
        standard error is raised.

    Returns:
        Path: The path to the created dump file.
    """
    _extra_name = extra_name or f"{datetime.now():%Y-%m-%d_%H-%M-%S}"
    filename = BACKUP_DIR / f"{postgres_name}_{_extra_name}.dump"

    cmd = [
        "pg_dump",
        "-h",
        postgres_host,
        "-p",
        str(postgres_port),
        "-U",
        postgres_user,
        "-F",
        "c",
        "-f",
        str(filename),
        postgres_name,
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = postgres_password

    process = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

    return filename
