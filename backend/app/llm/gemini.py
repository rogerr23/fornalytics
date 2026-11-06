"""Gemini adapter (google-genai SDK). Translates SDK errors into app errors."""

import logging
from collections.abc import AsyncIterator, Iterator, Sequence
from contextlib import contextmanager
from typing import Any

from google import genai
from google.genai import errors, types
from pydantic import BaseModel

from app.llm.base import ChatMessage, LLMProvider, parse_json_output
from app.llm.errors import (
    InvalidModelOutput,
    LLMError,
    Overloaded,
    ProviderNotConfigured,
    ProviderUnavailable,
    RateLimited,
    RetryableError,
)

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_MS = 120_000


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str, client: genai.Client | None = None) -> None:
        if not api_key:
            raise ProviderNotConfigured("Chave do Gemini ausente. Preencha GEMINI_API_KEY no .env.")
        if not model:
            raise ProviderNotConfigured("Modelo do Gemini ausente. Preencha GEMINI_MODEL no .env.")
        self.model = model
        self._client = client or genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=REQUEST_TIMEOUT_MS,
                # Our RetryingProvider handles 429s; the SDK must not retry on its own.
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

    async def generate(self, system: str, messages: Sequence[ChatMessage]) -> str:
        with self._translate_errors():
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=_to_contents(messages),
                config=types.GenerateContentConfig(system_instruction=system),
            )
        if not response.text:
            raise InvalidModelOutput()
        return response.text

    async def stream(self, system: str, messages: Sequence[ChatMessage]) -> AsyncIterator[str]:
        with self._translate_errors():
            chunks = await self._client.aio.models.generate_content_stream(
                model=self.model,
                contents=_to_contents(messages),
                config=types.GenerateContentConfig(system_instruction=system),
            )
            async for chunk in chunks:
                if chunk.text:
                    yield chunk.text

    async def generate_json[T: BaseModel](
        self, system: str, messages: Sequence[ChatMessage], schema: type[T]
    ) -> T:
        with self._translate_errors():
            response = await self._client.aio.models.generate_content(
                model=self.model,
                contents=_to_contents(messages),
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    response_mime_type="application/json",
                    response_schema=schema,
                ),
            )
        return parse_json_output(response.text or "", schema)

    @contextmanager
    def _translate_errors(self) -> Iterator[None]:
        try:
            yield
        except errors.APIError as exc:
            raise self._from_api_error(exc) from exc
        except (LLMError, RetryableError):
            raise
        except Exception as exc:
            # Network failures (timeouts, DNS, connection reset). Log only the type: no secrets.
            logger.warning("Gemini request failed: %s", type(exc).__name__)
            raise ProviderUnavailable(
                "Não foi possível falar com o Gemini. Tente de novo."
            ) from exc

    def _from_api_error(self, exc: errors.APIError) -> Exception:
        logger.warning("Gemini API error: %s %s", exc.code, exc.status)
        if exc.code == 429:
            return RateLimited(_retry_delay_seconds(exc.details))
        if exc.code in (401, 403) or (exc.code == 400 and "API key" in (exc.message or "")):
            return ProviderNotConfigured("A chave do Gemini foi recusada. Confira GEMINI_API_KEY.")
        if exc.code == 404:
            return ProviderNotConfigured(
                f"Modelo '{self.model}' não encontrado no Gemini. Confira GEMINI_MODEL "
                "(npm run llm:models lista os disponíveis)."
            )
        if isinstance(exc, errors.ServerError):
            # 503 "high demand" is common on the free tier and usually passes in seconds.
            return Overloaded(_retry_delay_seconds(exc.details))
        return LLMError()


def _to_contents(messages: Sequence[ChatMessage]) -> list[types.Content]:
    return [
        types.Content(
            role="model" if message.role == "assistant" else "user",
            parts=[types.Part(text=message.content)],
        )
        for message in messages
    ]


def _retry_delay_seconds(details: Any) -> float | None:
    """Read google.rpc.RetryInfo ("retryDelay": "37s") from an error body, if present."""
    error = details.get("error", details) if isinstance(details, dict) else {}
    for item in error.get("details", []) if isinstance(error, dict) else []:
        delay = item.get("retryDelay") if isinstance(item, dict) else None
        if isinstance(delay, str) and delay.endswith("s"):
            try:
                return float(delay.removesuffix("s"))
            except ValueError:
                return None
    return None
