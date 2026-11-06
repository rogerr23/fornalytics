import uuid
from datetime import UTC, datetime

from app.domain.enums import FeatureStatus, Lens, MessageRole, SourceType
from app.domain.lenses import StoredMessage
from app.domain.product_base import Evidence, Feature, ProductBase
from app.domain.projects import StoredFile
from app.ingestion.tokens import estimate_tokens
from app.lenses.context import rank_files, recent_history, select_chat_files, words


def stored(path: str, content: str) -> StoredFile:
    return StoredFile(
        path=path,
        content=content,
        token_estimate=estimate_tokens(content),
        source_type=SourceType.CODE,
    )


def base_citing(path: str, name: str) -> ProductBase:
    evidence = Evidence(source_type=SourceType.CODE, path=path, line_start=1, line_end=1, quote="x")
    return ProductBase(
        summary="",
        stack=[],
        entities=[],
        integrations=[],
        features=[
            Feature(
                name=name,
                description="",
                status=FeatureStatus.IMPLEMENTED,
                promise_ref="",
                evidence=[evidence],
            )
        ],
        flows=[],
        business_rules=[],
    )


FILES = [
    stored("src/payment/gateway.py", "def charge(order):\n    ..."),
    stored("src/cart.py", "def add_item():\n    # payment happens later\n"),
    stored("src/checkout.py", "def finish(order):\n    return charge(order)\n"),
    stored("README.md", "# Loja"),
]
EMPTY_BASE = base_citing("nada.py", "Nada")


def test_words_drop_accents_stopwords_and_short_words() -> None:
    assert words("Como funciona o Pagamento_online? É no checkout-v2") == {
        "pagamento",
        "online",
        "checkout",
    }


def test_path_match_weighs_more_than_content_match() -> None:
    ranked = rank_files("Como é o payment?", EMPTY_BASE, FILES)

    assert [file.path for _score, file in ranked] == ["src/payment/gateway.py", "src/cart.py"]


def test_files_cited_by_matching_base_items_rank_high() -> None:
    base = base_citing("src/checkout.py", "Finalizar compra com cupom")

    ranked = rank_files("tem cupom na compra?", base, FILES)

    assert ranked[0][1].path == "src/checkout.py"


def test_question_without_useful_words_selects_nothing() -> None:
    assert (
        select_chat_files("como isso funciona?", EMPTY_BASE, FILES, max_files=8, max_tokens=999)
        == []
    )


def test_selection_stops_at_the_first_limit() -> None:
    files = [stored(f"src/payment_{n}.py", "payment\n" * 100) for n in range(5)]
    each = files[0].token_estimate

    by_count = select_chat_files("payment", EMPTY_BASE, files, max_files=2, max_tokens=10_000)
    by_tokens = select_chat_files("payment", EMPTY_BASE, files, max_files=8, max_tokens=each * 3)

    assert len(by_count) == 2
    assert len(by_tokens) == 3


def message(role: MessageRole, content: str) -> StoredMessage:
    return StoredMessage(
        id=uuid.uuid4(),
        lens=Lens.TECNICO,
        role=role,
        content=content,
        citations=[],
        created_at=datetime.now(UTC),
    )


def test_history_keeps_last_complete_exchanges() -> None:
    user, assistant = MessageRole.USER, MessageRole.ASSISTANT
    messages = [
        message(assistant, "resposta órfã"),
        message(user, "p1"),
        message(assistant, "r1"),
        message(user, "p2 sem resposta"),
        message(user, "p3"),
        message(assistant, "r3"),
    ]

    history = recent_history(messages, turns=1)
    longer = recent_history(messages, turns=6)

    assert [(m.role, m.content) for m in history] == [("user", "p3"), ("assistant", "r3")]
    assert [m.content for m in longer] == ["p1", "r1", "p3", "r3"]
    assert recent_history(messages, turns=0) == []
