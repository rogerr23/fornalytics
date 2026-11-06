"""Extractor registry: one extractor per file format, chosen by extension."""

from pathlib import PurePosixPath
from typing import Protocol

from app.ingestion.errors import InvalidUpload
from app.ingestion.extractors.docx import DocxExtractor
from app.ingestion.extractors.pdf import PdfExtractor
from app.ingestion.extractors.text import TextExtractor
from app.ingestion.extractors.zip import ZipExtractor
from app.ingestion.types import ExtractionResult, UploadLimits


class Extractor(Protocol):
    extensions: tuple[str, ...]

    def extract(self, filename: str, data: bytes, limits: UploadLimits) -> ExtractionResult: ...


_EXTRACTORS: tuple[Extractor, ...] = (
    ZipExtractor(),
    PdfExtractor(),
    DocxExtractor(),
    TextExtractor(),
)
REGISTRY: dict[str, Extractor] = {ext: e for e in _EXTRACTORS for ext in e.extensions}
SUPPORTED_EXTENSIONS = tuple(sorted(REGISTRY))


def extension_of(filename: str) -> str:
    return PurePosixPath(filename.lower()).suffix


def get_extractor(filename: str) -> Extractor:
    extractor = REGISTRY.get(extension_of(filename))
    if extractor is None:
        supported = ", ".join(SUPPORTED_EXTENSIONS)
        raise InvalidUpload(f"Formato não suportado. Envie um destes: {supported}.")
    return extractor
