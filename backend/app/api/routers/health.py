"""Health check: tells the frontend (and humans) whether the API, database and LLM are set up."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine

from app import __version__
from app.api.deps import get_optional_engine
from app.core.config import Settings, get_settings
from app.db.health import DatabaseStatus, check_database
from app.llm.factory import LLMStatus, provider_status

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    database: DatabaseStatus
    llm: LLMStatus


@router.get("/health")
async def health(
    engine: Annotated[AsyncEngine | None, Depends(get_optional_engine)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        database=await check_database(engine),
        # Only reads .env: checking the model itself would spend quota on every page load.
        llm=provider_status(settings),
    )
