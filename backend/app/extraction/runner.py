"""Runs the extraction in the backend's own process, in the background (no external queue).

Every step is written to projects.status / status_detail, so reloading the page loses nothing.
"""

import asyncio
import logging
import uuid

from app.core.errors import AppError
from app.db.session import SessionFactory
from app.extraction.extractor import ProductBaseExtractor
from app.extraction.service import ProductBaseService
from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)

UNEXPECTED_ERROR = "Erro inesperado ao montar a base. Tente reprocessar."


class ProcessingRunner:
    def __init__(
        self,
        session_factory: SessionFactory,
        provider: LLMProvider,
        extractor: ProductBaseExtractor,
    ) -> None:
        self._session_factory = session_factory
        self._provider = provider
        self._extractor = extractor
        # Strong references: asyncio only keeps weak ones to running tasks.
        self._tasks: set[asyncio.Task[None]] = set()

    def submit(self, project_id: uuid.UUID) -> None:
        task = asyncio.create_task(self.run(project_id), name=f"process-{project_id}")
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def run(self, project_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            service = ProductBaseService(session)
            try:
                files = await service.load_files(project_id)

                async def progress(detail: str) -> None:
                    await service.report_progress(project_id, detail)

                outcome = await self._extractor.extract(files, progress)
                await service.save(project_id, outcome, self._provider.name, self._provider.model)
                logger.info(
                    "Project %s processed: mode=%s calls=%d dropped_citations=%d",
                    project_id,
                    outcome.mode,
                    outcome.model_calls,
                    outcome.dropped_citations,
                )
            except AppError as exc:
                logger.warning("Project %s failed: %s", project_id, type(exc).__name__)
                await service.fail(project_id, exc.message)
            except Exception:
                logger.exception("Project %s failed unexpectedly", project_id)
                await service.fail(project_id, UNEXPECTED_ERROR)

    async def wait_idle(self) -> None:
        """Wait for every submitted task (used by tests)."""
        while self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def shutdown(self) -> None:
        """Cancel running work; the next startup marks those projects as failed."""
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)


async def recover_interrupted(session_factory: SessionFactory) -> None:
    async with session_factory() as session:
        count = await ProductBaseService(session).recover_interrupted()
    if count:
        logger.warning("%d project(s) left in processing were marked as failed", count)
