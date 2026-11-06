"""FastAPI dependencies: one place to build what routers and services need."""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import DatabaseNotConfigured, SessionFactory, get_engine, get_sessionmaker
from app.extraction.extractor import ProductBaseExtractor
from app.extraction.runner import ProcessingRunner
from app.extraction.service import ProductBaseService
from app.ingestion.service import IngestionService
from app.lenses.chat import ChatService
from app.lenses.overview import OverviewService
from app.llm.base import LLMProvider
from app.llm.factory import create_provider
from app.projects.service import ProjectService
from app.prompts.builder import PromptBuilder


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as session:
        yield session


def get_optional_engine() -> AsyncEngine | None:
    """Engine, or None when DATABASE_URL is empty (the API still starts without a database)."""
    try:
        return get_engine()
    except DatabaseNotConfigured:
        return None


@lru_cache
def get_llm_provider() -> LLMProvider:
    """One provider per process. Raises ProviderNotConfigured (503) if .env is incomplete."""
    return create_provider(get_settings())


def get_session_factory() -> SessionFactory:
    """For work outside the request (background processing, SSE): one short session each."""
    return get_sessionmaker()


@lru_cache
def get_processing_runner() -> ProcessingRunner:
    """One runner per process: it keeps track of the extraction tasks still running."""
    settings = get_settings()
    provider = get_llm_provider()
    extractor = ProductBaseExtractor(provider, PromptBuilder(), settings.max_context_tokens)
    return ProcessingRunner(get_session_factory(), provider, extractor)


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_project_service(session: SessionDep, settings: SettingsDep) -> ProjectService:
    return ProjectService(session, settings)


def get_ingestion_service(session: SessionDep, settings: SettingsDep) -> IngestionService:
    return IngestionService(session, settings)


def get_product_base_service(session: SessionDep) -> ProductBaseService:
    return ProductBaseService(session)


SessionsDep = Annotated[SessionFactory, Depends(get_session_factory)]
ProviderDep = Annotated[LLMProvider, Depends(get_llm_provider)]


def get_overview_service(sessions: SessionsDep, provider: ProviderDep) -> OverviewService:
    return OverviewService(sessions, provider, PromptBuilder())


def get_chat_service(
    sessions: SessionsDep, provider: ProviderDep, settings: SettingsDep
) -> ChatService:
    return ChatService(sessions, provider, PromptBuilder(), settings)
