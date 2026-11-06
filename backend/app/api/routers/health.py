"""Health check: tells the frontend (and humans) that the API and the database are up."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine

from app import __version__
from app.api.deps import get_optional_engine
from app.db.health import DatabaseStatus, check_database

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str
    database: DatabaseStatus


@router.get("/health")
async def health(
    engine: Annotated[AsyncEngine | None, Depends(get_optional_engine)],
) -> HealthResponse:
    return HealthResponse(status="ok", version=__version__, database=await check_database(engine))
