import uuid

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LensCache
from app.domain.enums import CacheKind, Lens


class LensCacheRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, project_id: uuid.UUID, lens: Lens, kind: CacheKind) -> str | None:
        return await self._session.scalar(
            select(LensCache.content).where(
                LensCache.project_id == project_id,
                LensCache.lens == lens,
                LensCache.kind == kind,
            )
        )

    async def put(self, project_id: uuid.UUID, lens: Lens, kind: CacheKind, content: str) -> None:
        """First writer wins: two openings at the same time keep the first answer."""
        await self._session.execute(
            insert(LensCache)
            .values(project_id=project_id, lens=lens, kind=kind, content=content)
            .on_conflict_do_nothing()
        )

    async def clear(self, project_id: uuid.UUID) -> None:
        await self._session.execute(delete(LensCache).where(LensCache.project_id == project_id))
