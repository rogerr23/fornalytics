import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LensCache


class LensCacheRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def clear(self, project_id: uuid.UUID) -> None:
        await self._session.execute(delete(LensCache).where(LensCache.project_id == project_id))
