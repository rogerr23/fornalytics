"""Product base use case: start processing, save the result, read the base."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.lens_cache import LensCacheRepository
from app.db.repositories.product_bases import ProductBaseRepository
from app.db.repositories.projects import ProjectRepository
from app.db.repositories.sources import SourceRepository
from app.domain.enums import ProjectStatus
from app.domain.product_base import StoredProductBase
from app.domain.projects import Project, StoredFile
from app.extraction.errors import BaseNotFound, NothingToProcess
from app.extraction.extractor import ExtractionOutcome

QUEUED_DETAIL = "Na fila para processar"
INTERRUPTED_DETAIL = (
    "O servidor foi reiniciado durante o processamento. Clique em Reprocessar para tentar de novo."
)


class ProductBaseService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._projects = ProjectRepository(session)
        self._sources = SourceRepository(session)
        self._bases = ProductBaseRepository(session)
        self._cache = LensCacheRepository(session)

    async def start(self, project_id: uuid.UUID) -> Project:
        """Validate and mark the project as processing. The work itself runs in the background."""
        await self._projects.get(project_id)
        if not await self._sources.file_refs(project_id):
            raise NothingToProcess()
        project = await self._projects.start_processing(project_id, QUEUED_DETAIL)
        await self._session.commit()
        return project

    async def load_files(self, project_id: uuid.UUID) -> list[StoredFile]:
        files = await self._sources.files(project_id)
        # End the read transaction: model calls take long and must not hold a connection.
        await self._session.commit()
        return files

    async def report_progress(self, project_id: uuid.UUID, detail: str) -> None:
        await self._projects.set_status(project_id, ProjectStatus.PROCESSING, detail)
        await self._session.commit()

    async def save(
        self, project_id: uuid.UUID, outcome: ExtractionOutcome, provider: str, model: str
    ) -> None:
        """New base, empty lens cache and fresh flags in one transaction."""
        await self._bases.replace(project_id, outcome.base, provider, model)
        await self._cache.clear(project_id)
        await self._projects.set_status(
            project_id, ProjectStatus.READY, _ready_detail(outcome), base_outdated=False
        )
        await self._session.commit()

    async def fail(self, project_id: uuid.UUID, message: str) -> None:
        await self._session.rollback()
        await self._projects.set_status(project_id, ProjectStatus.FAILED, message)
        await self._session.commit()

    async def recover_interrupted(self) -> int:
        count = await self._projects.fail_interrupted(INTERRUPTED_DETAIL)
        await self._session.commit()
        return count

    async def get(self, project_id: uuid.UUID) -> tuple[Project, StoredProductBase]:
        project = await self._projects.get(project_id)
        base = await self._bases.get(project_id)
        if base is None:
            raise BaseNotFound()
        return project, base


def _ready_detail(outcome: ExtractionOutcome) -> str:
    features = len(outcome.base.features)
    parts = [f"Base pronta: {features} funcionalidade{'s' if features != 1 else ''}"]
    if outcome.dropped_citations:
        parts.append(f"{outcome.dropped_citations} citação(ões) descartada(s) por não conferir")
    if outcome.excluded_files:
        parts.append(f"{outcome.excluded_files} arquivo(s) fora do limite")
    return "; ".join(parts) + "."
