import uuid
from typing import Any

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, UUIDPrimaryKey, text_enum
from app.domain.enums import CacheKind, Lens


class LensCache(CreatedAt, Base):
    """Cached lens output (e.g. overview). Cleared when the project is reprocessed."""

    __tablename__ = "lens_cache"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    lens: Mapped[Lens] = mapped_column(text_enum(Lens, "lens"), primary_key=True)
    kind: Mapped[CacheKind] = mapped_column(text_enum(CacheKind, "cache_kind"), primary_key=True)
    content: Mapped[str] = mapped_column(Text)


class Comparison(UUIDPrimaryKey, CreatedAt, Base):
    """Idea × Code result. One per project; cleared when the project is reprocessed."""

    __tablename__ = "comparisons"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), unique=True
    )
    product_base_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_bases.id", ondelete="CASCADE"), index=True
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSONB)
