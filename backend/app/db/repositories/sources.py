import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.db.models import Source, SourceFile
from app.domain.enums import SourceType
from app.domain.projects import FileRef, SourceSummary, StoredFile


class SourceNotFound(NotFound):
    def __init__(self) -> None:
        super().__init__("Fonte não encontrada neste projeto.")


class FileNotFound(NotFound):
    def __init__(self, path: str) -> None:
        super().__init__(f"Arquivo '{path}' não encontrado neste projeto.")


class SourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        project_id: uuid.UUID,
        source_type: SourceType,
        filename: str | None,
        files: Sequence[StoredFile],
    ) -> uuid.UUID:
        source = Source(project_id=project_id, type=source_type, filename=filename)
        self._session.add(source)
        await self._session.flush()
        self._session.add_all(
            SourceFile(
                source_id=source.id,
                path=file.path,
                content=file.content,
                token_estimate=file.token_estimate,
            )
            for file in files
        )
        await self._session.flush()
        return source.id

    async def summaries(self, project_id: uuid.UUID) -> list[SourceSummary]:
        query = (
            select(
                Source.id,
                Source.type,
                Source.filename,
                Source.created_at,
                func.count(SourceFile.id).label("file_count"),
                func.coalesce(func.sum(SourceFile.token_estimate), 0).label("token_estimate"),
            )
            .outerjoin(SourceFile, SourceFile.source_id == Source.id)
            .where(Source.project_id == project_id)
            .group_by(Source.id)
            .order_by(Source.created_at)
        )
        rows = await self._session.execute(query)
        return [SourceSummary.model_validate(row._mapping) for row in rows]

    async def delete(self, project_id: uuid.UUID, source_id: uuid.UUID) -> None:
        source = await self._session.get(Source, source_id)
        if source is None or source.project_id != project_id:
            raise SourceNotFound()
        await self._session.delete(source)
        await self._session.flush()

    async def file_refs(self, project_id: uuid.UUID) -> list[FileRef]:
        query = (
            select(SourceFile.path, SourceFile.token_estimate, Source.type.label("source_type"))
            .join(Source, SourceFile.source_id == Source.id)
            .where(Source.project_id == project_id)
        )
        rows = await self._session.execute(query)
        return [FileRef.model_validate(row._mapping) for row in rows]

    async def files(
        self, project_id: uuid.UUID, paths: Sequence[str] | None = None
    ) -> list[StoredFile]:
        """Stored files of the project, with content; only `paths` when given."""
        query = (
            select(
                SourceFile.path,
                SourceFile.content,
                SourceFile.token_estimate,
                Source.type.label("source_type"),
            )
            .join(Source, SourceFile.source_id == Source.id)
            .where(Source.project_id == project_id)
        )
        if paths is not None:
            query = query.where(SourceFile.path.in_(list(paths)))
        rows = await self._session.execute(query)
        return [StoredFile.model_validate(row._mapping) for row in rows]

    async def get_file(self, project_id: uuid.UUID, path: str) -> StoredFile:
        query = (
            select(
                SourceFile.path,
                SourceFile.content,
                SourceFile.token_estimate,
                Source.type.label("source_type"),
            )
            .join(Source, SourceFile.source_id == Source.id)
            .where(Source.project_id == project_id, SourceFile.path == path)
        )
        row = (await self._session.execute(query)).first()
        if row is None:
            raise FileNotFound(path)
        return StoredFile.model_validate(row._mapping)
