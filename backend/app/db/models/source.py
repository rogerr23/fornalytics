import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, CreatedAt, UUIDPrimaryKey, text_enum
from app.domain.enums import SourceType


class Source(UUIDPrimaryKey, CreatedAt, Base):
    """One uploaded file or pasted text."""

    __tablename__ = "sources"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[SourceType] = mapped_column(text_enum(SourceType, "source_type"))
    filename: Mapped[str | None] = mapped_column(String(255))


class SourceFile(UUIDPrimaryKey, Base):
    """Extracted text of one file inside a source (a zip yields many)."""

    __tablename__ = "source_files"
    __table_args__ = (UniqueConstraint("source_id", "path"),)

    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), index=True
    )
    path: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    token_estimate: Mapped[int]
