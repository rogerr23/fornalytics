from app.domain.enums import SourceType
from app.domain.projects import FileRef
from app.ingestion.limits import compute_limits
from app.ingestion.rendering import render_file
from app.ingestion.tokens import estimate_tokens


def code(path: str, tokens: int) -> FileRef:
    return FileRef(path=path, token_estimate=tokens, source_type=SourceType.CODE)


def test_priority_cut_keeps_important_files_and_lists_the_rest() -> None:
    files = [
        code("src/utils/huge_helpers.py", 80),
        code("README.md", 10),
        code("src/routes/checkout.py", 30),
        code("src/utils/small.py", 5),
    ]

    limits = compute_limits(files, budget=50)

    assert [f.path for f in limits.code.excluded] == ["src/utils/huge_helpers.py"]
    assert limits.code.included_tokens == 45  # README + route + the small file still fit
    assert limits.code.total_tokens == 125


def test_documents_and_code_have_separate_budgets() -> None:
    files = [
        code("src/app.py", 40),
        FileRef(path="escopo.pdf", token_estimate=40, source_type=SourceType.IDEA_DOC),
    ]

    limits = compute_limits(files, budget=50)

    assert limits.code.excluded == []
    assert limits.documents.excluded == []


def test_numbered_rendering_and_token_estimate() -> None:
    assert render_file("src/a.py", "import os\nprint(1)") == (
        "=== src/a.py ===\n1| import os\n2| print(1)"
    )
    assert estimate_tokens("a" * 9) == 3
