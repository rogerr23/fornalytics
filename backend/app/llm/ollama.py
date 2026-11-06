"""Ollama adapter (local HTTP API). Fallback provider, selected manually in .env."""

import json
import logging
from collections.abc import AsyncIterator, Iterator, Sequence
from contextlib import contextmanager
from typing import Any

import httpx
from pydantic import BaseModel

from app.llm.base import ChatMessage, LLMProvider, parse_json_output
from app.llm.errors import (
    InvalidModelOutput,
    LLMError,
    ProviderNotConfigured,
    ProviderUnavailable,
    RateLimited,
    RetryableError,
)

logger = logging.getLogger(__name__)

# Local models can be slow on modest hardware.
TIMEOUT = httpx.Timeout(300.0, connect=5.0)


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str, model: str, client: httpx.AsyncClient | None = None) -> None:
        if not model:
            raise ProviderNotConfigured("Modelo do Ollama ausente. Preencha OLLAMA_MODEL no .env.")
        self.model = model
        self._base_url = base_url
        self._client = client or httpx.AsyncClient(base_url=base_url, timeout=TIMEOUT)

    async def generate(self, system: str, messages: Sequence[ChatMessage]) -> str:
        data = await self._post(self._payload(system, messages, stream=False))
        return _message_content(data)

    async def stream(self, system: str, messages: Sequence[ChatMessage]) -> AsyncIterator[str]:
        payload = self._payload(system, messages, stream=True)
        with self._translate_errors():
            async with self._client.stream("POST", "/api/chat", json=payload) as response:
                await self._raise_for_status(response)
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if "error" in data:
                        raise ProviderUnavailable(f"Erro do Ollama: {data['error']}")
                    if content := data.get("message", {}).get("content"):
                        yield content
                    if data.get("done"):
                        return

    async def generate_json[T: BaseModel](
        self, system: str, messages: Sequence[ChatMessage], schema: type[T]
    ) -> T:
        payload = self._payload(system, messages, stream=False)
        payload["format"] = schema.model_json_schema()
        data = await self._post(payload)
        return parse_json_output(_message_content(data), schema)

    async def aclose(self) -> None:
        await self._client.aclose()

    def _payload(
        self, system: str, messages: Sequence[ChatMessage], *, stream: bool
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [{"role": "system", "content": system}]
            + [message.model_dump() for message in messages],
            "stream": stream,
        }

    async def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self._translate_errors():
            response = await self._client.post("/api/chat", json=payload)
            await self._raise_for_status(response)
            return response.json()

    async def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        await response.aread()
        if response.status_code == 429:
            raise RateLimited()
        if response.status_code == 404:
            raise ProviderNotConfigured(
                f"Modelo '{self.model}' não encontrado no Ollama. Rode: ollama pull {self.model}"
            )
        raise ProviderUnavailable(f"O Ollama respondeu com erro {response.status_code}.")

    @contextmanager
    def _translate_errors(self) -> Iterator[None]:
        try:
            yield
        except (LLMError, RetryableError):
            raise
        except httpx.ConnectError as exc:
            raise ProviderUnavailable(
                f"O Ollama não está rodando em {self._base_url}. Abra o Ollama e tente de novo."
            ) from exc
        except httpx.HTTPError as exc:
            logger.warning("Ollama request failed: %s", type(exc).__name__)
            raise ProviderUnavailable(
                "Não foi possível falar com o Ollama. Tente de novo."
            ) from exc


def _message_content(data: dict[str, Any]) -> str:
    content = data.get("message", {}).get("content")
    if not isinstance(content, str) or not content:
        raise InvalidModelOutput()
    return content
