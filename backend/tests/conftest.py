"""Shared fixtures. Database tests run on the Neon test branch and are skipped without it."""

from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import create_engine

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = get_settings().test_database_url
    if not url:
        pytest.skip("TEST_DATABASE_URL não configurada: testes de banco pulados.")
    return url


@pytest.fixture(scope="session")
def migrated_database(test_database_url: str) -> str:
    """Apply migrations once per test run (no-op when already up to date)."""
    config = Config(BACKEND_DIR / "alembic.ini")
    config.attributes["database_url"] = test_database_url
    command.upgrade(config, "head")
    return test_database_url


@pytest.fixture
async def db_session(migrated_database: str) -> AsyncIterator[AsyncSession]:
    """Session inside a transaction that is rolled back after the test: nothing is persisted."""
    engine = create_engine(migrated_database, pooled=False)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()
