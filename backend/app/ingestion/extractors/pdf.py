import io
import logging

import pdfplumber

from app.ingestion.errors import InvalidUpload
from app.ingestion.extractors.text import single_file
from app.ingestion.types import ExtractionResult, UploadLimits

logger = logging.getLogger(__name__)


class PdfExtractor:
    extensions = (".pdf",)

    def extract(self, filename: str, data: bytes, limits: UploadLimits) -> ExtractionResult:
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
        except Exception as exc:
            logger.info("Unreadable PDF: %s", type(exc).__name__)
            raise InvalidUpload("Não foi possível ler o PDF. Ele pode estar corrompido.") from exc
        if not any(page.strip() for page in pages):
            raise InvalidUpload(
                "O PDF não tem texto selecionável (provavelmente é escaneado). "
                "Envie a versão em texto."
            )
        # Page markers let citations point to a page.
        text = "\n".join(
            f"--- página {number} ---\n{page.strip()}" for number, page in enumerate(pages, 1)
        )
        return single_file(filename, text)
