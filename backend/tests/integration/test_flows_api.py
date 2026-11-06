import uuid

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm_provider
from app.db.repositories.product_bases import ProductBaseRepository
from app.domain.product_base import BaseFlow, ProductBase
from app.llm.fake import FakeProvider
from tests.fixtures.builders import make_zip

BASE = ProductBase(
    summary="Loja",
    stack=[],
    entities=[],
    integrations=[],
    features=[],
    flows=[BaseFlow(name="Comprar", steps=["Escolhe o produto", "Paga"], evidence=[])],
    business_rules=[],
)

FLOW = """{"name": "Adicionar ao carrinho",
 "steps": [{"text": "Chama add_item.", "evidence": [
   {"source_type": "code", "path": "src/routes/cart.py", "line_start": 1, "line_end": 2,
    "quote": "def add_item"}]}],
 "nodes": [{"id": "a", "label": "Clica em \\"comprar\\""}, {"id": "b", "label": "Item salvo"}],
 "edges": [{"source": "a", "target": "b", "label": "ok"}]}"""


@pytest.fixture
async def project_id(api: httpx.AsyncClient, db_session: AsyncSession) -> str:
    project_id = (await api.post("/projects", json={"name": "Loja"})).json()["id"]
    await api.post(
        f"/projects/{project_id}/sources",
        data={"type": "code"},
        files={
            "file": (
                "loja.zip",
                make_zip({"loja/src/routes/cart.py": "def add_item():\n    return 'ok'\n"}),
                "application/zip",
            )
        },
    )
    await ProductBaseRepository(db_session).replace(uuid.UUID(project_id), BASE, "fake", "fake")
    await db_session.flush()
    return project_id


async def test_base_flows_need_no_model(
    app: FastAPI, api: httpx.AsyncClient, project_id: str
) -> None:
    app.dependency_overrides[get_llm_provider] = lambda: FakeProvider()  # no queued answer

    response = await api.get(f"/projects/{project_id}/flows")

    [flow] = response.json()
    assert flow["name"] == "Comprar"
    assert flow["mermaid"].endswith("n1 --> n2")


async def test_asked_flow_comes_with_built_mermaid_and_checked_evidence(
    app: FastAPI, api: httpx.AsyncClient, project_id: str
) -> None:
    provider = FakeProvider([FLOW])
    app.dependency_overrides[get_llm_provider] = lambda: provider

    response = await api.post(
        f"/projects/{project_id}/flow",
        json={"question": "O que acontece ao comprar?", "lens": "tecnico"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["mermaid"] == (
        'flowchart TD\n    n1["Clica em #quot;comprar#quot;"]\n'
        '    n2["Item salvo"]\n    n1 -->|"ok"| n2'
    )
    assert body["steps"][0]["evidence"][0]["path"] == "src/routes/cart.py"
    assert "Tarefa: explicar um fluxo" in provider.calls[0].system


async def test_flows_need_a_processed_project(app: FastAPI, api: httpx.AsyncClient) -> None:
    app.dependency_overrides[get_llm_provider] = lambda: FakeProvider()
    project_id = (await api.post("/projects", json={"name": "Sem base"})).json()["id"]

    listed = await api.get(f"/projects/{project_id}/flows")
    asked = await api.post(
        f"/projects/{project_id}/flow", json={"question": "Como compra?", "lens": "cliente"}
    )

    assert (listed.status_code, asked.status_code) == (409, 409)
