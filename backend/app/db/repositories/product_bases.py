import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ProductBase as ProductBaseRow
from app.domain.product_base import ProductBase, StoredProductBase


class ProductBaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, project_id: uuid.UUID) -> StoredProductBase | None:
        row = await self._session.scalar(
            select(ProductBaseRow).where(ProductBaseRow.project_id == project_id)
        )
        if row is None:
            return None
        return StoredProductBase(
            data=ProductBase.model_validate(row.data),
            provider=row.provider,
            model=row.model,
            created_at=row.created_at,
        )

    async def replace(
        self, project_id: uuid.UUID, base: ProductBase, provider: str, model: str
    ) -> None:
        """One base per project: insert, or overwrite the previous one."""
        values = {
            "data": base.model_dump(mode="json"),
            "provider": provider,
            "model": model,
        }
        statement = insert(ProductBaseRow).values(id=uuid.uuid4(), project_id=project_id, **values)
        statement = statement.on_conflict_do_update(
            index_elements=[ProductBaseRow.project_id],
            set_={**values, "created_at": func.now()},
        )
        await self._session.execute(statement)
