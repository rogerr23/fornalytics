import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Response, UploadFile, status

from app.api.deps import SettingsDep, get_ingestion_service, get_project_service
from app.api.schemas.projects import FileContentOut, IngestionSummaryOut, SourceOut
from app.domain.enums import SourceType
from app.ingestion.errors import InvalidUpload, UploadTooLarge
from app.ingestion.service import IngestionService
from app.projects.service import ProjectService

router = APIRouter(prefix="/projects/{project_id}", tags=["sources"])

Ingestion = Annotated[IngestionService, Depends(get_ingestion_service)]
Projects = Annotated[ProjectService, Depends(get_project_service)]

READ_CHUNK_BYTES = 1024 * 1024


@router.post("/sources", status_code=status.HTTP_201_CREATED)
async def add_source(
    project_id: uuid.UUID,
    service: Ingestion,
    settings: SettingsDep,
    type: Annotated[SourceType, Form()],
    file: UploadFile | None = None,
    title: Annotated[str | None, Form()] = None,
    content: Annotated[str | None, Form()] = None,
    url: Annotated[str | None, Form(max_length=500)] = None,
) -> IngestionSummaryOut:
    """Send a file (zip, pdf, docx, md, txt), a public GitHub repository link or pasted text.

    Text is extracted right away.
    """
    if file is not None and file.filename:
        data = await _read_limited(file, settings.max_upload_mb)
        summary = await service.ingest_upload(project_id, type, file.filename, data)
    elif url and url.strip():
        if type != SourceType.CODE:
            raise InvalidUpload("Link do GitHub é sempre código: use o tipo 'code'.")
        summary = await service.ingest_github(project_id, url)
    elif content and content.strip():
        summary = await service.ingest_text(project_id, type, title, content)
    else:
        raise InvalidUpload("Envie um arquivo, um link do GitHub ou cole um texto.")
    return IngestionSummaryOut.model_validate(summary.model_dump())


@router.get("/sources")
async def list_sources(project_id: uuid.UUID, service: Projects) -> list[SourceOut]:
    detail = await service.detail(project_id)
    return [SourceOut.model_validate(s.model_dump()) for s in detail.sources]


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    project_id: uuid.UUID, source_id: uuid.UUID, service: Ingestion
) -> Response:
    await service.delete_source(project_id, source_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/files")
async def get_file(
    project_id: uuid.UUID, path: Annotated[str, Query(min_length=1)], service: Projects
) -> FileContentOut:
    """Full text of one stored file (used to open citations)."""
    file = await service.file(project_id, path)
    return FileContentOut(
        path=file.path,
        source_type=file.source_type,
        line_count=file.content.count("\n") + 1,
        content=file.content,
    )


async def _read_limited(file: UploadFile, max_mb: int) -> bytes:
    max_bytes = max_mb * 1024 * 1024
    buffer = bytearray()
    while chunk := await file.read(READ_CHUNK_BYTES):
        buffer.extend(chunk)
        if len(buffer) > max_bytes:
            raise UploadTooLarge(f"O arquivo passa de {max_mb} MB (MAX_UPLOAD_MB).")
    return bytes(buffer)
