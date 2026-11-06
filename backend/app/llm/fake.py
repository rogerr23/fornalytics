"""Scripted provider for tests: no network, no quota."""

import re
from collections import deque
from collections.abc import AsyncIterator, Iterable, Sequence
from dataclasses import dataclass

from pydantic import BaseModel

from app.llm.base import ChatMessage, LLMProvider, parse_json_output

FakeResponse = str | BaseModel | Exception


@dataclass(frozen=True)
class FakeCall:
    method: str
    system: str
    messages: tuple[ChatMessage, ...]


class FakeProvider(LLMProvider):
    """Returns queued responses in order and records every call.

    A queued Exception is raised instead of returned (to simulate failures).
    """

    name = "fake"
    model = "fake-model"

    def __init__(self, responses: Iterable[FakeResponse] = ()) -> None:
        self._responses: deque[FakeResponse] = deque(responses)
        self.calls: list[FakeCall] = []

    async def generate(self, system: str, messages: Sequence[ChatMessage]) -> str:
        return self._next_text("generate", system, messages)

    async def stream(self, system: str, messages: Sequence[ChatMessage]) -> AsyncIterator[str]:
        text = self._next_text("stream", system, messages)
        for chunk in re.findall(r"\S+\s*", text):
            yield chunk

    async def generate_json[T: BaseModel](
        self, system: str, messages: Sequence[ChatMessage], schema: type[T]
    ) -> T:
        return parse_json_output(self._next_text("generate_json", system, messages), schema)

    def _next_text(self, method: str, system: str, messages: Sequence[ChatMessage]) -> str:
        self.calls.append(FakeCall(method, system, tuple(messages)))
        if not self._responses:
            raise AssertionError("FakeProvider has no more queued responses")
        response = self._responses.popleft()
        if isinstance(response, Exception):
            raise response
        if isinstance(response, BaseModel):
            return response.model_dump_json()
        return response
