import pytest

from app.ingestion.errors import InvalidUpload
from app.ingestion.extractors import get_extractor
from app.ingestion.types import UploadLimits
from tests.fixtures.builders import make_docx, make_pdf

LIMITS = UploadLimits(max_unzipped_bytes=1024, max_files=1)


def extract_text(filename: str, data: bytes) -> str:
    result = get_extractor(filename).extract(filename, data, LIMITS)
    assert len(result.files) == 1
    return result.files[0].content


def test_pdf_text_keeps_page_markers() -> None:
    text = extract_text("escopo.pdf", make_pdf(["Catalogo de produtos", "Emissao de nota fiscal"]))

    assert text.splitlines() == [
        "--- página 1 ---",
        "Catalogo de produtos",
        "--- página 2 ---",
        "Emissao de nota fiscal",
    ]


def test_pdf_without_text_is_rejected_with_explanation() -> None:
    with pytest.raises(InvalidUpload, match="escaneado"):
        extract_text("scan.pdf", make_pdf([""]))


def test_docx_paragraphs_and_tables() -> None:
    data = make_docx(["Escopo da loja", "Cupom de desconto"], table=[["Item", "Prazo"]])

    text = extract_text("escopo.docx", data)

    assert "Escopo da loja\nCupom de desconto" in text
    assert "Item | Prazo" in text


def test_unsupported_format_lists_the_accepted_ones() -> None:
    with pytest.raises(InvalidUpload, match=".zip"):
        get_extractor("planilha.xlsx")
