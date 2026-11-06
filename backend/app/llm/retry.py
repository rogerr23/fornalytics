"""Retry temporary failures (429 and 5xx), wrapping any provider (Decorator pattern)."""

import asyncio
import random
from collections.abc import AsyncIterator, Awaitable, Callable, Sequence

from pydantic import BaseModel

from app.llm.base import ChatMessage, LLMProvider
from app.llm.errors import RetryableError

MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 2.0
MAX_JITTER_SECONDS = 0.5
# Waiting longer than this would freeze the screen: tell the user instead.
MAX_WAIT_SECONDS = 30.0

Sleep = Callable[[float], Awaitable[None]]


def next_delay(attempt: int, exc: RetryableError, attempts: int = MAX_ATTEMPTS) -> float:
    """Seconds to wait before attempt `attempt + 1`, or raise the user-facing error to give up."""
    if exc.retry_after is not None:
        delay = exc.retry_after
    else:
        delay = BASE_DELAY_SECONDS * 2 ** (attempt - 1) + random.uniform(0, MAX_JITTER_SECONDS)
    if attempt >= attempts or delay > MAX_WAIT_SECONDS:
        raise exc.give_up() from exc
    return delay


class RetryingProvider(LLMProvider):
    def __init__(self, inner: LLMProvider, *, sleep: Sleep = asyncio.sleep) -> None:
        self.inner = inner
        self.name = inner.name
        self.model = inner.model
        self._sleep = sleep

    async def _call[R](self, call: Callable[[], Awaitable[R]]) -> R:
        attempt = 1
        while True:
            try:
                return await call()
            except RetryableError as exc:
                await self._sleep(next_delay(attempt, exc))
                attempt += 1

    async def generate(self, system: str, messages: Sequence[ChatMessage]) -> str:
        return await self._call(lambda: self.inner.generate(system, messages))

    async def generate_json[T: BaseModel](
        self, system: str, messages: Sequence[ChatMessage], schema: type[T]
    ) -> T:
        return await self._call(lambda: self.inner.generate_json(system, messages, schema))

    async def stream(self, system: str, messages: Sequence[ChatMessage]) -> AsyncIterator[str]:
        attempt = 1
        while True:
            started = False
            try:
                async for chunk in self.inner.stream(system, messages):
                    started = True
                    yield chunk
                return
            except RetryableError as exc:
                # Retrying after text reached the screen would duplicate it.
                if started:
                    raise exc.give_up() from exc
                await self._sleep(next_delay(attempt, exc))
                attempt += 1

    async def aclose(self) -> None:
        await self.inner.aclose()
