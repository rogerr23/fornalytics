import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.repositories.projects import ProjectRepository
from app.db.repositories.sources import SourceRepository
from app.domain.projects import ContextLimits, Project, SourceSummary, StoredFile
from app.ingestion.limits import compute_limits


class ProjectDetail(BaseModel):
    project: Project
    sources: list[SourceSummary]
    limits: ContextLimits


class ProjectService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._projects = ProjectRepository(session)
        self._sources = SourceRepository(session)

    async def create(self, name: str) -> Project:
        project = await self._projects.create(name.strip())
        await self._session.commit()
        return project

    async def list(self) -> list[Project]:
        return await self._projects.list()

    async def detail(self, project_id: uuid.UUID) -> ProjectDetail:
        project = await self._projects.get(project_id)
        return ProjectDetail(
            project=project,
            sources=await self._sources.summaries(project_id),
            limits=await self.limits(project_id),
        )

    async def limits(self, project_id: uuid.UUID) -> ContextLimits:
        refs = await self._sources.file_refs(project_id)
        return compute_limits(refs, self._settings.max_context_tokens)

    async def file(self, project_id: uuid.UUID, path: str) -> StoredFile:
        await self._projects.get(project_id)
        return await self._sources.get_file(project_id, path)
