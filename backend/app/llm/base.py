"""The single interface every model provider implements."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Sequence
from typing import Literal

from pydantic import BaseModel, ValidationError

from app.llm.errors import InvalidModelOutput


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class LLMProvider(ABC):
    """A model provider (Gemini, Ollama, and in the future Claude)."""

    name: str
    model: str

    @abstractmethod
    async def generate(self, system: str, messages: Sequence[ChatMessage]) -> str:
        """Return the full answer as text."""

    @abstractmethod
    def stream(self, system: str, messages: Sequence[ChatMessage]) -> AsyncIterator[str]:
        """Yield the answer in chunks as the model produces it."""

    @abstractmethod
    async def generate_json[T: BaseModel](
        self, system: str, messages: Sequence[ChatMessage], schema: type[T]
    ) -> T:
        """Return structured output validated against `schema`."""

    async def aclose(self) -> None:  # noqa: B027 (optional hook, empty by default)
        """Release network resources. Default: nothing to release."""


def parse_json_output[T: BaseModel](text: str, schema: type[T]) -> T:
    """Validate model output against the schema; any mismatch is an InvalidModelOutput."""
    try:
        return schema.model_validate_json(text)
    except ValidationError as exc:
        raise InvalidModelOutput() from exc
