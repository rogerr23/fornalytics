"""Database reachability check used by the health endpoint."""

import asyncio
import logging
from typing import Literal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)

DatabaseStatus = Literal["ok", "unavailable", "not_configured"]

# A sleeping serverless database may take a moment to wake up.
CHECK_TIMEOUT_SECONDS = 5


async def check_database(engine: AsyncEngine | None) -> DatabaseStatus:
    if engine is None:
        return "not_configured"
    try:
        async with asyncio.timeout(CHECK_TIMEOUT_SECONDS), engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:  # any failure means "unavailable"
        # Log only the exception type: driver messages may contain the connection URL.
        logger.warning("Database health check failed: %s", type(exc).__name__)
        return "unavailable"
    return "ok"
