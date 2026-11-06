"""Async engine and session factory."""

from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.errors import AppError

ASYNC_DRIVER_PREFIX = "postgresql+psycopg://"

# Opens a short session (work outside the request: background processing, SSE streams).
SessionFactory = Callable[[], AbstractAsyncContextManager[AsyncSession]]


class DatabaseNotConfigured(AppError):
    status_code = 503

    def __init__(self) -> None:
        super().__init__("Banco de dados não configurado. Preencha DATABASE_URL no arquivo .env.")


def to_async_url(url: str) -> str:
    """Accept URLs as providers hand them out (postgresql://...) and select the psycopg driver."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return ASYNC_DRIVER_PREFIX + url.removeprefix(prefix)
    return url


def create_engine(url: str, *, pooled: bool = True) -> AsyncEngine:
    return create_async_engine(
        to_async_url(url),
        # Connection poolers (PgBouncer) do not support prepared statements.
        connect_args={"prepare_threshold": None},
        # Idle serverless databases drop connections; test before reuse.
        pool_pre_ping=True,
        **({} if pooled else {"poolclass": NullPool}),
    )


@lru_cache
def get_engine() -> AsyncEngine:
    url = get_settings().database_url
    if not url:
        raise DatabaseNotConfigured()
    return create_engine(url)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)
