"""Ingestion use case: extract text on upload, store it, and report what happened."""

import asyncio
import re
import uuid
from collections import defaultdict
from pathlib import PurePosixPath

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import Conflict
from app.db.repositories.projects import ProjectRepository
from app.db.repositories.sources import SourceRepository
from app.domain.enums import ProjectStatus, SourceType
from app.domain.projects import ContextLimits, StoredFile
from app.ingestion.errors import InvalidUpload
from app.ingestion.extractors import extension_of, get_extractor
from app.ingestion.extractors.text import single_file
from app.ingestion.filters import MAX_FILE_BYTES
from app.ingestion.limits import compute_limits
from app.ingestion.tokens import estimate_tokens
from app.ingestion.types import ExtractionResult, SkipReason, UploadLimits

MAX_SKIP_EXAMPLES = 5

SKIP_LABELS = {
    SkipReason.IGNORED_DIR: "em pasta ignorada",
    SkipReason.LOCKFILE: "lockfile",
    SkipReason.BINARY: "binário ou imagem",
    SkipReason.MINIFIED: "minificado",
    SkipReason.TOO_LARGE: "acima de 200 KB",
    SkipReason.SECRET: "possível segredo (.env, chave)",
    SkipReason.UNSAFE_PATH: "caminho inseguro (../ ou absoluto)",
    SkipReason.EMPTY: "vazio",
}

ARCHIVE_TYPES = frozenset({SourceType.CODE})
DOCUMENT_TYPES = frozenset({SourceType.IDEA_DOC, SourceType.TRANSCRIPT})
PASTED_TYPES = frozenset({SourceType.TEXT, SourceType.TRANSCRIPT})


class SkippedGroup(BaseModel):
    reason: SkipReason
    count: int
    examples: list[str]


class RenamedPath(BaseModel):
    original: str
    stored_as: str


class IngestedFile(BaseModel):
    path: str
    token_estimate: int


class IngestionSummary(BaseModel):
    source_id: uuid.UUID
    source_type: SourceType
    filename: str | None
    files: list[IngestedFile]
    token_estimate: int
    skipped: list[SkippedGroup]
    renamed: list[RenamedPath]
    base_outdated: bool
    limits: ContextLimits


class IngestionService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._projects = ProjectRepository(session)
        self._sources = SourceRepository(session)

    async def ingest_upload(
        self, project_id: uuid.UUID, source_type: SourceType, filename: str, data: bytes
    ) -> IngestionSummary:
        _check_type_for_file(filename, source_type)
        await self._ensure_editable(project_id)
        limits = UploadLimits(
            max_unzipped_bytes=self._settings.max_unzipped_mb * 1024 * 1024,
            max_files=self._settings.max_files,
        )
        extractor = get_extractor(filename)
        # Parsing PDFs and zips is CPU work: keep the event loop free.
        result = await asyncio.to_thread(extractor.extract, filename, data, limits)
        return await self._store(project_id, source_type, PurePosixPath(filename).name, result)

    async def ingest_text(
        self, project_id: uuid.UUID, source_type: SourceType, title: str | None, content: str
    ) -> IngestionSummary:
        if source_type not in PASTED_TYPES:
            raise InvalidUpload("Texto colado deve ter tipo 'text' ou 'transcript'.")
        if len(content.encode()) > MAX_FILE_BYTES:
            raise InvalidUpload("Texto acima de 200 KB. Divida em partes menores.")
        await self._ensure_editable(project_id)
        result = single_file(_text_path(title), content.replace("\r\n", "\n"))
        return await self._store(project_id, source_type, None, result)

    async def delete_source(self, project_id: uuid.UUID, source_id: uuid.UUID) -> None:
        await self._ensure_editable(project_id)
        await self._sources.delete(project_id, source_id)
        if await self._projects.has_base(project_id):
            await self._projects.mark_base_outdated(project_id)
        await self._session.commit()

    async def _ensure_editable(self, project_id: uuid.UUID) -> None:
        project = await self._projects.get(project_id)
        if project.status == ProjectStatus.PROCESSING:
            raise Conflict(
                "O projeto está sendo processado. Aguarde terminar para mudar o material."
            )

    async def _store(
        self,
        project_id: uuid.UUID,
        source_type: SourceType,
        filename: str | None,
        result: ExtractionResult,
    ) -> IngestionSummary:
        if not result.files:
            reasons = ", ".join(
                f"{group.count} {SKIP_LABELS[group.reason]}" for group in _group_skipped(result)
            )
            raise InvalidUpload(
                f"Nenhum arquivo de texto aproveitável foi encontrado. Ignorados: {reasons}."
            )
        taken = {ref.path for ref in await self._sources.file_refs(project_id)}
        files: list[StoredFile] = []
        renamed: list[RenamedPath] = []
        for extracted in result.files:
            path = _unique_path(extracted.path, taken)
            taken.add(path)
            if path != extracted.path:
                renamed.append(RenamedPath(original=extracted.path, stored_as=path))
            files.append(
                StoredFile(
                    path=path,
                    content=extracted.content,
                    token_estimate=estimate_tokens(extracted.content),
                    source_type=source_type,
                )
            )

        source_id = await self._sources.add(project_id, source_type, filename, files)
        if await self._projects.has_base(project_id):
            await self._projects.mark_base_outdated(project_id)
        await self._session.commit()

        project = await self._projects.get(project_id)
        refs = await self._sources.file_refs(project_id)
        return IngestionSummary(
            source_id=source_id,
            source_type=source_type,
            filename=filename,
            files=[IngestedFile(path=f.path, token_estimate=f.token_estimate) for f in files],
            token_estimate=sum(f.token_estimate for f in files),
            skipped=_group_skipped(result),
            renamed=renamed,
            base_outdated=project.base_outdated,
            limits=compute_limits(refs, self._settings.max_context_tokens),
        )


def _check_type_for_file(filename: str, source_type: SourceType) -> None:
    if extension_of(filename) == ".zip":
        if source_type not in ARCHIVE_TYPES:
            raise InvalidUpload("Arquivo .zip é sempre código: use o tipo 'code'.")
    elif source_type not in DOCUMENT_TYPES:
        raise InvalidUpload(
            "Documentos (PDF, .docx, .md, .txt) devem ter tipo 'idea_doc' ou 'transcript'. "
            "Código é enviado como .zip."
        )


def _text_path(title: str | None) -> str:
    cleaned = re.sub(r"[^\w\- ]+", "", (title or "").strip()).strip()
    return f"{cleaned or 'texto-colado'}.txt"


def _unique_path(path: str, taken: set[str]) -> str:
    """README.md -> README (2).md when the path already exists in the project."""
    if path not in taken:
        return path
    pure = PurePosixPath(path)
    number = 2
    while True:
        candidate = str(pure.with_name(f"{pure.stem} ({number}){pure.suffix}"))
        if candidate not in taken:
            return candidate
        number += 1


def _group_skipped(result: ExtractionResult) -> list[SkippedGroup]:
    groups: dict[SkipReason, list[str]] = defaultdict(list)
    for skipped in result.skipped:
        groups[skipped.reason].append(skipped.path)
    return [
        SkippedGroup(reason=reason, count=len(paths), examples=paths[:MAX_SKIP_EXAMPLES])
        for reason, paths in sorted(groups.items(), key=lambda item: -len(item[1]))
    ]
