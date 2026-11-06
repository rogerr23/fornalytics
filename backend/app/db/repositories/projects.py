import uuid

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Conflict, NotFound
from app.db.models import ProductBase
from app.db.models import Project as ProjectRow
from app.domain.enums import ProjectStatus
from app.domain.projects import Project


class ProjectNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__("Projeto não encontrado.")


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, name: str) -> Project:
        row = ProjectRow(name=name)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return Project.model_validate(row)

    async def list(self) -> list[Project]:
        rows = await self._session.scalars(
            select(ProjectRow).order_by(ProjectRow.created_at.desc())
        )
        return [Project.model_validate(row) for row in rows]

    async def get(self, project_id: uuid.UUID) -> Project:
        return Project.model_validate(await self._get_row(project_id))

    async def has_base(self, project_id: uuid.UUID) -> bool:
        return bool(
            await self._session.scalar(select(exists().where(ProductBase.project_id == project_id)))
        )

    async def mark_base_outdated(self, project_id: uuid.UUID) -> None:
        row = await self._get_row(project_id)
        row.base_outdated = True
        await self._session.flush()

    async def start_processing(self, project_id: uuid.UUID, detail: str) -> Project:
        """Move to `processing` atomically: two clicks at the same time cannot both start."""
        result = await self._session.execute(
            update(ProjectRow)
            .where(ProjectRow.id == project_id, ProjectRow.status != ProjectStatus.PROCESSING)
            .values(status=ProjectStatus.PROCESSING, status_detail=detail)
            .returning(ProjectRow.id)
        )
        if result.scalar_one_or_none() is None:
            await self.get(project_id)  # raises ProjectNotFound when it does not exist
            raise Conflict("O projeto já está sendo processado. Acompanhe o progresso.")
        row = await self._get_row(project_id)
        await self._session.refresh(row)
        return Project.model_validate(row)

    async def set_status(
        self,
        project_id: uuid.UUID,
        status: ProjectStatus,
        detail: str | None,
        *,
        base_outdated: bool | None = None,
    ) -> None:
        row = await self._get_row(project_id)
        row.status = status
        row.status_detail = detail
        if base_outdated is not None:
            row.base_outdated = base_outdated
        await self._session.flush()

    async def fail_interrupted(self, detail: str) -> int:
        """Projects left in `processing` (the server stopped mid-way) become `failed`."""
        result = await self._session.execute(
            update(ProjectRow)
            .where(ProjectRow.status == ProjectStatus.PROCESSING)
            .values(status=ProjectStatus.FAILED, status_detail=detail)
            .returning(ProjectRow.id)
        )
        return len(result.all())

    async def _get_row(self, project_id: uuid.UUID) -> ProjectRow:
        row = await self._session.get(ProjectRow, project_id)
        if row is None:
            raise ProjectNotFound()
        return row
