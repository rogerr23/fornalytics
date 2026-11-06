import json
import uuid
from typing import Any

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm_provider
from app.db.repositories.product_bases import ProductBaseRepository
from app.domain.enums import FeatureStatus, SourceType
from app.domain.product_base import Evidence, Feature, ProductBase
from app.llm.errors import QuotaExceeded
from app.llm.fake import FakeProvider, FakeResponse
from tests.fixtures.builders import make_zip

ZIP = make_zip(
    {
        "loja/src/routes/cart.py": "def add_item():\n    return 'ok'\n",
        "loja/src/payment.py": "def charge():\n    ...\n",
    }
)

BASE = ProductBase(
    summary="Uma loja.",
    stack=["Python"],
    entities=["Carrinho"],
    integrations=[],
    features=[
        Feature(
            name="Carrinho",
            description="Adiciona itens ao carrinho",
            status=FeatureStatus.IMPLEMENTED,
            promise_ref="",
            evidence=[
                Evidence(
                    source_type=SourceType.CODE,
                    path="src/routes/cart.py",
                    line_start=1,
                    line_end=2,
                    quote="def add_item",
                )
            ],
        )
    ],
    flows=[],
    business_rules=[],
)

ANSWER = "O carrinho fica em [[src/routes/cart.py:L1-L2]] e em [[src/inventado.py:L1]]."


def sse(text: str) -> list[tuple[str, dict[str, Any]]]:
    """Parse an SSE body into (event, data) pairs."""
    events = []
    for block in text.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines() if not line.startswith(":"))
        events.append((lines["event"], json.loads(lines["data"])))
    return events


@pytest.fixture
def use_provider(app: FastAPI):  # noqa: ANN201
    def install(responses: list[FakeResponse]) -> FakeProvider:
        provider = FakeProvider(responses)
        app.dependency_overrides[get_llm_provider] = lambda: provider
        return provider

    return install


async def project_with_base(api: httpx.AsyncClient, db_session: AsyncSession) -> str:
    project_id = (await api.post("/projects", json={"name": "Loja"})).json()["id"]
    await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "code"},
        files={"file": ("loja.zip", ZIP, "application/zip")},
    )
    await ProductBaseRepository(db_session).replace(uuid.UUID(project_id), BASE, "fake", "fake")
    await db_session.flush()
    return project_id


async def test_overview_is_generated_once_then_served_from_cache(
    api: httpx.AsyncClient, db_session: AsyncSession, use_provider
) -> None:
    provider = use_provider([ANSWER])
    project_id = await project_with_base(api, db_session)

    first = await api.get(f"/projects/{project_id}/overview", params={"lens": "tecnico"})
    second = await api.get(f"/projects/{project_id}/overview", params={"lens": "tecnico"})

    first_events = sse(first.text)
    assert "".join(data["text"] for name, data in first_events if name == "delta") == ANSWER
    name, data = first_events[-2]
    assert name == "citations"
    assert [(c["path"], c["valid"]) for c in data["citations"]] == [
        ("src/routes/cart.py", True),
        ("src/inventado.py", False),
    ]
    assert first_events[-1] == ("done", {"cached": False, "message_id": None})

    assert sse(second.text)[0] == ("delta", {"text": ANSWER})
    assert sse(second.text)[-1][1]["cached"] is True
    assert len(provider.calls) == 1
    assert "Lente: técnico" in provider.calls[0].system
    assert "Tarefa: visão geral" in provider.calls[0].system
    assert '"name":"Carrinho"' in provider.calls[0].messages[0].content


async def test_chat_streams_saves_messages_and_sends_history(
    api: httpx.AsyncClient, db_session: AsyncSession, use_provider
) -> None:
    provider = use_provider([ANSWER, "Não encontrei no material."])
    project_id = await project_with_base(api, db_session)

    first = sse(
        (
            await api.post(
                f"/projects/{project_id}/chat",
                json={"lens": "tecnico", "question": "Como funciona o carrinho?"},
            )
        ).text
    )
    conversation_id = first[0][1]["conversation_id"]
    second = sse(
        (
            await api.post(
                f"/projects/{project_id}/chat",
                json={
                    "lens": "cliente",
                    "question": "Tem nota fiscal?",
                    "conversation_id": conversation_id,
                },
            )
        ).text
    )

    assert [name for name, _ in first][0] == "conversation"
    assert first[-1][0] == "done" and first[-1][1]["message_id"]
    assert second[-2] == ("citations", {"citations": []})

    first_call, second_call = provider.calls
    assert "=== src/routes/cart.py ===" in first_call.messages[-1].content
    assert "Lente: cliente" in second_call.system
    assert [m.role for m in second_call.messages] == ["user", "assistant", "user"]
    assert second_call.messages[1].content == ANSWER

    conversation = (await api.get(f"/projects/{project_id}/conversations/{conversation_id}")).json()
    assert [(m["role"], m["lens"]) for m in conversation["messages"]] == [
        ("user", "tecnico"),
        ("assistant", "tecnico"),
        ("user", "cliente"),
        ("assistant", "cliente"),
    ]
    assert [c["valid"] for c in conversation["messages"][1]["citations"]] == [True, False]


async def test_quota_error_during_chat_becomes_an_error_event(
    api: httpx.AsyncClient, db_session: AsyncSession, use_provider
) -> None:
    use_provider([QuotaExceeded(30)])
    project_id = await project_with_base(api, db_session)

    response = await api.post(
        f"/projects/{project_id}/chat", json={"lens": "nao_tecnico", "question": "O que faz?"}
    )
    events = sse(response.text)

    assert response.status_code == 200
    assert events[-1][0] == "error"
    assert "limite gratuito" in events[-1][1]["message"]
    conversation_id = events[0][1]["conversation_id"]
    conversation = (await api.get(f"/projects/{project_id}/conversations/{conversation_id}")).json()
    assert [m["role"] for m in conversation["messages"]] == ["user"]


async def test_lenses_need_a_processed_project(api: httpx.AsyncClient, use_provider) -> None:
    use_provider([])
    project_id = (await api.post("/projects", json={"name": "Sem base"})).json()["id"]

    overview = await api.get(f"/projects/{project_id}/overview", params={"lens": "cliente"})
    chat = await api.post(
        f"/projects/{project_id}/chat", json={"lens": "cliente", "question": "Oi?"}
    )
    unknown = await api.get(f"/projects/{project_id}/conversations/{uuid.uuid4()}")

    assert overview.status_code == 409
    assert chat.status_code == 409
    assert unknown.status_code == 404


async def test_compare_answers_in_three_lenses_with_one_call(
    api: httpx.AsyncClient, db_session: AsyncSession, use_provider
) -> None:
    provider = use_provider(
        [
            '{"cliente": "Você adiciona itens.", "nao_tecnico": "O carrinho guarda os itens.",'
            ' "tecnico": "Rota em [[src/routes/cart.py:L1-L2]] e [[src/x.py:L1]]."}'
        ]
    )
    project_id = await project_with_base(api, db_session)

    response = await api.post(
        f"/projects/{project_id}/compare-lenses", json={"question": "Como funciona o carrinho?"}
    )

    body = response.json()
    assert response.status_code == 200
    assert [a["lens"] for a in body["answers"]] == ["cliente", "nao_tecnico", "tecnico"]
    assert [c["valid"] for c in body["answers"][2]["citations"]] == [True, False]
    assert len(provider.calls) == 1
    assert all(f"Lente: {n}" in provider.calls[0].system for n in ("cliente", "técnico"))


async def test_does_it_verdict_follows_the_base(
    api: httpx.AsyncClient, db_session: AsyncSession, use_provider
) -> None:
    use_provider(
        [
            '{"verdict": "nao", "feature_name": "Carrinho", "justification": "Não faz.",'
            ' "evidence": []}'
        ]
    )
    project_id = await project_with_base(api, db_session)

    response = await api.post(
        f"/projects/{project_id}/does-it",
        json={"question": "Tem carrinho?", "lens": "nao_tecnico"},
    )

    body = response.json()
    assert body["verdict"] == "sim"
    assert body["adjusted"] is True
    assert body["feature"] == {"name": "Carrinho", "status": "implemented"}
    assert [e["path"] for e in body["evidence"]] == ["src/routes/cart.py"]


async def test_one_shot_questions_need_a_processed_project(
    api: httpx.AsyncClient, use_provider
) -> None:
    use_provider([])
    project_id = (await api.post("/projects", json={"name": "Sem base"})).json()["id"]

    compare = await api.post(f"/projects/{project_id}/compare-lenses", json={"question": "Oi?"})
    does_it = await api.post(
        f"/projects/{project_id}/does-it", json={"question": "Faz?", "lens": "cliente"}
    )

    assert (compare.status_code, does_it.status_code) == (409, 409)
