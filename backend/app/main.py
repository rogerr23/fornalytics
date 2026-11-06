"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.deps import get_llm_provider, get_processing_runner
from app.api.routers import health, processing, projects, sources
from app.core.config import Settings, get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import setup_logging
from app.db.session import DatabaseNotConfigured, get_engine, get_sessionmaker
from app.extraction.runner import recover_interrupted

API_PREFIX = "/api"

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await _recover_interrupted_processing()
    yield
    if get_processing_runner.cache_info().currsize:
        await get_processing_runner().shutdown()
    # Close pooled connections on shutdown, for whatever was actually created.
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
    if get_llm_provider.cache_info().currsize:
        await get_llm_provider().aclose()


async def _recover_interrupted_processing() -> None:
    """Projects stuck in `processing` after a restart become `failed` (the API starts anyway)."""
    try:
        await recover_interrupted(get_sessionmaker())
    except DatabaseNotConfigured:
        return
    except Exception:
        logger.warning("Could not check for interrupted processing", exc_info=True)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    setup_logging()

    app = FastAPI(title="Fornalytics API", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(health.router, prefix=API_PREFIX)
    app.include_router(projects.router, prefix=API_PREFIX)
    app.include_router(sources.router, prefix=API_PREFIX)
    app.include_router(processing.router, prefix=API_PREFIX)
    return app


app = create_app()
