"""API contract for the lenses (DTOs, separate from the domain models)."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import Lens, MessageRole

MAX_QUESTION_CHARS = 2000


class ChatIn(BaseModel):
    lens: Lens
    question: str = Field(min_length=1, max_length=MAX_QUESTION_CHARS)
    # Empty to start a new conversation; the id comes back in the `conversation` event.
    conversation_id: uuid.UUID | None = None


class TextCitationOut(BaseModel):
    marker: str
    path: str
    line_start: int
    line_end: int
    valid: bool
    problem: str | None


class MessageOut(BaseModel):
    id: uuid.UUID
    lens: Lens
    role: MessageRole
    content: str
    citations: list[TextCitationOut]
    created_at: datetime


class ConversationOut(BaseModel):
    id: uuid.UUID
    messages: list[MessageOut]
