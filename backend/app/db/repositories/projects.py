import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.db.models import ProductBase
from app.db.models import Project as ProjectRow
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

    async def _get_row(self, project_id: uuid.UUID) -> ProjectRow:
        row = await self._session.get(ProjectRow, project_id)
        if row is None:
            raise ProjectNotFound()
        return row
