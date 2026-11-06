"""FastAPI dependencies: one place to build what routers and services need."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.db.session import DatabaseNotConfigured, get_engine, get_sessionmaker


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as session:
        yield session


def get_optional_engine() -> AsyncEngine | None:
    """Engine, or None when DATABASE_URL is empty (the API still starts without a database)."""
    try:
        return get_engine()
    except DatabaseNotConfigured:
        return None
