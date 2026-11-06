import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_processing_runner, get_product_base_service, get_session_factory
from app.api.schemas.product_base import ProcessingStatusOut, ProductBaseOut
from app.api.sse import sse_event, sse_heartbeat, sse_response
from app.db.session import SessionFactory
from app.domain.projects import Project
from app.extraction.runner import ProcessingRunner
from app.extraction.service import ProductBaseService
from app.extraction.status import watch_status

router = APIRouter(prefix="/projects/{project_id}", tags=["processing"])

Service = Annotated[ProductBaseService, Depends(get_product_base_service)]
Runner = Annotated[ProcessingRunner, Depends(get_processing_runner)]
Sessions = Annotated[SessionFactory, Depends(get_session_factory)]


@router.post("/process", status_code=status.HTTP_202_ACCEPTED)
async def process_project(
    project_id: uuid.UUID, service: Service, runner: Runner
) -> ProcessingStatusOut:
    """Start the AI extraction (promises + base) in the background. Follow it on /status."""
    project = await service.start(project_id)
    runner.submit(project_id)
    return _status(project)


@router.get("/status", response_class=StreamingResponse)
async def processing_status(project_id: uuid.UUID, sessions: Sessions) -> StreamingResponse:
    """SSE: one `status` event per change, until the project stops processing.

    Contract in docs/api-events.md.
    """
    updates = watch_status(sessions, project_id)
    # Read the first state before streaming, so an unknown project is a plain 404.
    first = await anext(updates)

    async def events() -> AsyncIterator[str]:
        if first is not None:
            yield sse_event("status", _status(first))
        async for project in updates:
            yield sse_heartbeat() if project is None else sse_event("status", _status(project))

    return sse_response(events())


@router.get("/base")
async def get_base(project_id: uuid.UUID, service: Service) -> ProductBaseOut:
    project, stored = await service.get(project_id)
    return ProductBaseOut.model_validate(
        {
            "provider": stored.provider,
            "model": stored.model,
            "created_at": stored.created_at,
            "base_outdated": project.base_outdated,
            **stored.data.model_dump(),
        }
    )


def _status(project: Project) -> ProcessingStatusOut:
    return ProcessingStatusOut(
        status=project.status,
        status_detail=project.status_detail,
        base_outdated=project.base_outdated,
    )
