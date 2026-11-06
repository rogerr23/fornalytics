import io
import logging

import docx

from app.ingestion.errors import InvalidUpload
from app.ingestion.extractors.text import single_file
from app.ingestion.types import ExtractionResult, UploadLimits

logger = logging.getLogger(__name__)


class DocxExtractor:
    extensions = (".docx",)

    def extract(self, filename: str, data: bytes, limits: UploadLimits) -> ExtractionResult:
        try:
            document = docx.Document(io.BytesIO(data))
        except Exception as exc:
            logger.info("Unreadable DOCX: %s", type(exc).__name__)
            raise InvalidUpload("Não foi possível ler o arquivo .docx.") from exc
        lines = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            lines.append("")
            lines.extend(" | ".join(cell.text.strip() for cell in row.cells) for row in table.rows)
        return single_file(filename, "\n".join(lines).strip())
