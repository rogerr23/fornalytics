"""Project, source and file data as the services see it (no ORM)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.domain.enums import ProjectStatus, SourceType

DOCUMENT_SOURCE_TYPES = frozenset({SourceType.IDEA_DOC, SourceType.TRANSCRIPT, SourceType.TEXT})


class _FromORM(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class Project(_FromORM):
    id: uuid.UUID
    name: str
    status: ProjectStatus
    status_detail: str | None
    base_outdated: bool
    created_at: datetime


class SourceSummary(_FromORM):
    id: uuid.UUID
    type: SourceType
    filename: str | None
    file_count: int
    token_estimate: int
    created_at: datetime


class FileRef(_FromORM):
    """A stored file without its content (cheap to list)."""

    path: str
    token_estimate: int
    source_type: SourceType


class StoredFile(FileRef):
    content: str


class GroupLimit(BaseModel):
    """How one extraction step (documents or code) fits in MAX_CONTEXT_TOKENS."""

    total_tokens: int
    included_tokens: int
    excluded: list[FileRef]


class ContextLimits(BaseModel):
    budget_per_step: int
    documents: GroupLimit
    code: GroupLimit
