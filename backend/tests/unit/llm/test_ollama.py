import json

import httpx
import pytest

from app.llm.base import ChatMessage
from app.llm.errors import ProviderNotConfigured, ProviderUnavailable
from app.llm.ollama import OllamaProvider

MESSAGES = [ChatMessage(role="user", content="oi")]
BASE_URL = "http://ollama.test"


def provider_with(handler: httpx.MockTransport) -> OllamaProvider:
    client = httpx.AsyncClient(base_url=BASE_URL, transport=handler)
    return OllamaProvider(BASE_URL, "llama-test", client=client)


async def test_stream_joins_ndjson_chunks() -> None:
    lines = [
        {"message": {"content": "Olá"}, "done": False},
        {"message": {"content": ", mundo"}, "done": False},
        {"message": {"content": ""}, "done": True},
    ]
    body = "\n".join(json.dumps(line) for line in lines)
    provider = provider_with(httpx.MockTransport(lambda _: httpx.Response(200, text=body)))

    chunks = [chunk async for chunk in provider.stream("sys", MESSAGES)]

    assert "".join(chunks) == "Olá, mundo"


async def test_ollama_not_running_is_a_friendly_error() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    provider = provider_with(httpx.MockTransport(refuse))

    with pytest.raises(ProviderUnavailable, match="não está rodando"):
        await provider.generate("sys", MESSAGES)


async def test_missing_model_tells_how_to_pull_it() -> None:
    provider = provider_with(
        httpx.MockTransport(lambda _: httpx.Response(404, json={"error": "model not found"}))
    )

    with pytest.raises(ProviderNotConfigured, match="ollama pull llama-test"):
        await provider.generate("sys", MESSAGES)
