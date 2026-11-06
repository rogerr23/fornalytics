"""API contract for projects and sources (DTOs, separate from the domain models)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ProjectStatus, SourceType
from app.ingestion.types import SkipReason


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str
    status: ProjectStatus
    status_detail: str | None
    base_outdated: bool
    created_at: datetime


class SourceOut(BaseModel):
    id: uuid.UUID
    type: SourceType
    filename: str | None
    file_count: int
    token_estimate: int
    created_at: datetime


class FileRefOut(BaseModel):
    path: str
    token_estimate: int
    source_type: SourceType


class GroupLimitOut(BaseModel):
    total_tokens: int
    included_tokens: int
    excluded: list[FileRefOut]


class LimitsOut(BaseModel):
    budget_per_step: int
    documents: GroupLimitOut
    code: GroupLimitOut


class ProjectDetailOut(ProjectOut):
    sources: list[SourceOut]
    limits: LimitsOut


class SkippedGroupOut(BaseModel):
    reason: SkipReason
    count: int
    examples: list[str]


class RenamedPathOut(BaseModel):
    original: str
    stored_as: str


class IngestedFileOut(BaseModel):
    path: str
    token_estimate: int


class IngestionSummaryOut(BaseModel):
    source_id: uuid.UUID
    source_type: SourceType
    filename: str | None
    files: list[IngestedFileOut]
    token_estimate: int
    skipped: list[SkippedGroupOut]
    renamed: list[RenamedPathOut]
    base_outdated: bool
    limits: LimitsOut


class FileContentOut(BaseModel):
    path: str
    source_type: SourceType
    line_count: int
    content: str
