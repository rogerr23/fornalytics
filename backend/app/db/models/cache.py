import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, text_enum
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
