"""Watch a project's processing status for the SSE endpoint."""

import asyncio
import uuid
from collections.abc import AsyncIterator

from app.db.repositories.projects import ProjectRepository
from app.db.session import SessionFactory
from app.domain.enums import ProjectStatus
from app.domain.projects import Project

POLL_SECONDS = 1.0
HEARTBEAT_SECONDS = 15.0
MAX_WATCH_SECONDS = 15 * 60


async def watch_status(
    session_factory: SessionFactory,
    project_id: uuid.UUID,
    *,
    poll_seconds: float = POLL_SECONDS,
) -> AsyncIterator[Project | None]:
    """Yield the project when its status changes and None as a heartbeat.

    Ends once the project is no longer processing. Each read uses a short session, so the
    stream never holds a database connection while it waits.
    """
    last: tuple[ProjectStatus, str | None] | None = None
    quiet = 0.0
    elapsed = 0.0
    while elapsed < MAX_WATCH_SECONDS:
        async with session_factory() as session:
            project = await ProjectRepository(session).get(project_id)
        current = (project.status, project.status_detail)
        if current != last:
            last = current
            quiet = 0.0
            yield project
        elif quiet >= HEARTBEAT_SECONDS:
            quiet = 0.0
            yield None
        if project.status != ProjectStatus.PROCESSING:
            return
        await asyncio.sleep(poll_seconds)
        quiet += poll_seconds
        elapsed += poll_seconds
