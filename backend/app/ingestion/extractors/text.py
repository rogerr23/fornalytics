from pathlib import PurePosixPath

from app.ingestion.errors import InvalidUpload
from app.ingestion.filters import MAX_FILE_BYTES
from app.ingestion.text import decode_text
from app.ingestion.types import ExtractedFile, ExtractionResult, UploadLimits


class TextExtractor:
    extensions = (".md", ".txt")

    def extract(self, filename: str, data: bytes, limits: UploadLimits) -> ExtractionResult:
        if len(data) > MAX_FILE_BYTES:
            raise InvalidUpload("Arquivo de texto acima de 200 KB. Divida em partes menores.")
        return single_file(filename, decode_text(data))


def single_file(filename: str, text: str) -> ExtractionResult:
    if not text.strip():
        raise InvalidUpload("O arquivo não tem texto aproveitável.")
    return ExtractionResult(files=[ExtractedFile(PurePosixPath(filename).name, text)])
