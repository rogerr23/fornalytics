import pytest

from app.domain.enums import FeatureStatus, SourceType
from app.domain.product_base import IdeaPromises, ProductBase
from app.domain.projects import StoredFile
from app.extraction.errors import NothingToProcess
from app.extraction.extractor import ProductBaseExtractor
from app.extraction.reconcile import ExtractionMode
from app.ingestion.tokens import estimate_tokens
from app.llm.errors import InvalidModelOutput, QuotaExceeded
from app.llm.fake import FakeProvider
from app.prompts.builder import PromptBuilder


def stored(path: str, content: str, source_type: SourceType) -> StoredFile:
    return StoredFile(
        path=path,
        content=content,
        token_estimate=estimate_tokens(content),
        source_type=source_type,
    )


CODE = stored("src/routes/cart.py", "def add_item():\n    return 'ok'\n", SourceType.CODE)
DOC = stored("escopo.md", "# Loja\nCarrinho de compras.\nCupom de desconto.", SourceType.IDEA_DOC)

PROMISES_JSON = """{"promises": [
  {"id": "P1", "name": "Carrinho", "description": "Adicionar itens",
   "evidence": [{"source_type": "idea_doc", "path": "escopo.md", "line_start": 2,
                 "line_end": 2, "quote": "Carrinho de compras."}]},
  {"id": "P2", "name": "Cupom", "description": "Desconto", "evidence": []}
]}"""

BASE_JSON = """{"summary": "Uma loja.", "stack": ["Python"], "entities": ["Carrinho"],
 "integrations": [],
 "features": [{"name": "Carrinho", "description": "Adiciona itens", "status": "implemented",
   "promise_ref": "P1",
   "evidence": [{"source_type": "code", "path": "src/routes/cart.py", "line_start": 1,
                 "line_end": 2, "quote": "def add_item():"}]}],
 "flows": [{"name": "Comprar", "steps": ["Adicionar item"],
   "evidence": [{"source_type": "code", "path": "src/routes/cart.py", "line_start": 9,
                 "line_end": 9, "quote": "checkout()"}]}],
 "business_rules": []}"""


async def no_progress(_detail: str) -> None:
    return None


def extractor(provider: FakeProvider, budget: int = 10_000) -> ProductBaseExtractor:
    return ProductBaseExtractor(provider, PromptBuilder(), budget)


async def test_idea_and_code_runs_two_steps_and_reconciles() -> None:
    provider = FakeProvider([PROMISES_JSON, BASE_JSON])
    steps: list[str] = []

    async def progress(detail: str) -> None:
        steps.append(detail)

    outcome = await extractor(provider).extract([DOC, CODE], progress)

    assert outcome.mode == ExtractionMode.CODE_WITH_PROMISES
    assert outcome.model_calls == 2
    assert [(f.name, f.status) for f in outcome.base.features] == [
        ("Carrinho", FeatureStatus.IMPLEMENTED),
        ("Cupom", FeatureStatus.DOCUMENTED_ONLY),
    ]
    assert outcome.dropped_citations == 1  # the flow cites a line that does not exist
    assert outcome.base.flows[0].evidence == []
    assert len(steps) == 3

    promises_call, base_call = provider.calls
    assert "Tarefa: promessas" in promises_call.system
    assert "=== escopo.md ===" in promises_call.messages[0].content
    assert "src/routes/cart.py" not in promises_call.messages[0].content
    assert "Tarefa: base do produto" in base_call.system
    assert base_call.messages[0].content.startswith("MODO: codigo_com_promessas")
    assert "- P2: Cupom — Desconto" in base_call.messages[0].content
    assert "1| def add_item():" in base_call.messages[0].content


@pytest.mark.parametrize(
    ("files", "mode", "header"),
    [
        ([CODE], ExtractionMode.CODE_ONLY, "=== src/routes/cart.py ==="),
        ([DOC], ExtractionMode.IDEA_ONLY, "=== escopo.md ==="),
    ],
)
async def test_single_kind_of_material_uses_one_call(
    files: list[StoredFile], mode: ExtractionMode, header: str
) -> None:
    provider = FakeProvider([BASE_JSON])

    outcome = await extractor(provider).extract(files, no_progress)

    assert outcome.mode == mode
    assert outcome.model_calls == 1
    assert provider.calls[0].messages[0].content.startswith(f"MODO: {mode.value}")
    assert header in provider.calls[0].messages[0].content


async def test_files_over_the_budget_are_not_sent_nor_citable() -> None:
    big = stored("src/zz_big.py", "x = 1\n" * 400, SourceType.CODE)
    provider = FakeProvider([BASE_JSON])

    outcome = await extractor(provider, budget=CODE.token_estimate).extract(
        [CODE, big], no_progress
    )

    assert outcome.excluded_files == 1
    assert "src/zz_big.py" not in provider.calls[0].messages[0].content


async def test_without_material_nothing_is_called() -> None:
    provider = FakeProvider()

    with pytest.raises(NothingToProcess):
        await extractor(provider).extract([], no_progress)
    assert provider.calls == []


@pytest.mark.parametrize(
    ("response", "error"),
    [('{"summary": "faltam campos"}', InvalidModelOutput), (QuotaExceeded(30), QuotaExceeded)],
)
async def test_model_errors_reach_the_caller(response: object, error: type[Exception]) -> None:
    provider = FakeProvider([response])  # type: ignore[list-item]

    with pytest.raises(error):
        await extractor(provider).extract([CODE], no_progress)


def test_schemas_parse_valid_model_output() -> None:
    assert len(IdeaPromises.model_validate_json(PROMISES_JSON).promises) == 2
    assert ProductBase.model_validate_json(BASE_JSON).features[0].promise_ref == "P1"
