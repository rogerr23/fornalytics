from collections.abc import AsyncIterator, Sequence

import pytest

from app.llm.base import ChatMessage
from app.llm.errors import Overloaded, ProviderUnavailable, QuotaExceeded, RateLimited
from app.llm.fake import FakeProvider
from app.llm.retry import MAX_ATTEMPTS, RetryingProvider

MESSAGES = [ChatMessage(role="user", content="oi")]


class SleepRecorder:
    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, delay: float) -> None:
        self.delays.append(delay)


async def test_retries_after_rate_limit_and_returns_answer() -> None:
    sleep = SleepRecorder()
    provider = RetryingProvider(FakeProvider([RateLimited(), "ok"]), sleep=sleep)

    assert await provider.generate("sys", MESSAGES) == "ok"
    assert len(sleep.delays) == 1


async def test_gives_up_after_max_attempts() -> None:
    sleep = SleepRecorder()
    provider = RetryingProvider(FakeProvider([RateLimited()] * MAX_ATTEMPTS), sleep=sleep)

    with pytest.raises(QuotaExceeded):
        await provider.generate("sys", MESSAGES)
    assert len(sleep.delays) == MAX_ATTEMPTS - 1


async def test_overloaded_provider_is_retried_then_reported_as_unavailable() -> None:
    sleep = SleepRecorder()
    provider = RetryingProvider(FakeProvider([Overloaded()] * MAX_ATTEMPTS), sleep=sleep)

    with pytest.raises(ProviderUnavailable, match="alta demanda"):
        await provider.generate("sys", MESSAGES)
    assert len(sleep.delays) == MAX_ATTEMPTS - 1


async def test_long_server_delay_fails_fast_with_wait_time() -> None:
    sleep = SleepRecorder()
    provider = RetryingProvider(FakeProvider([RateLimited(retry_after=60)]), sleep=sleep)

    with pytest.raises(QuotaExceeded, match="60 segundos"):
        await provider.generate("sys", MESSAGES)
    assert sleep.delays == []


async def test_stream_retries_when_rate_limited_before_first_chunk() -> None:
    sleep = SleepRecorder()
    provider = RetryingProvider(FakeProvider([RateLimited(), "olá mundo"]), sleep=sleep)

    chunks = [chunk async for chunk in provider.stream("sys", MESSAGES)]

    assert "".join(chunks) == "olá mundo"
    assert len(sleep.delays) == 1


class FailsMidStream(FakeProvider):
    async def stream(self, system: str, messages: Sequence[ChatMessage]) -> AsyncIterator[str]:
        yield "começo "
        raise RateLimited()


async def test_stream_does_not_retry_after_text_was_sent() -> None:
    sleep = SleepRecorder()
    provider = RetryingProvider(FailsMidStream(), sleep=sleep)

    received: list[str] = []
    with pytest.raises(QuotaExceeded):
        async for chunk in provider.stream("sys", MESSAGES):
            received.append(chunk)
    assert received == ["começo "]
    assert sleep.delays == []


@pytest.mark.parametrize(
    ("retry_after", "expected"),
    [
        (30, "Tente de novo em 30 segundos."),
        (300, "Tente de novo em 5 minutos."),
        (52323, "limite diário do plano gratuito: tente de novo em cerca de 15 horas."),
    ],
)
def test_quota_message_shows_a_readable_wait(retry_after: float, expected: str) -> None:
    assert QuotaExceeded(retry_after).message.endswith(expected)
