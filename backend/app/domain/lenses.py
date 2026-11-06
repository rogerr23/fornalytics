"""What the lenses produce: streamed text, text citations and chat messages."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import Lens, MessageRole


class TextCitation(BaseModel):
    """A [[path:Lx-Ly]] marker found in a model answer, after checking it."""

    marker: str
    path: str
    line_start: int
    line_end: int
    valid: bool
    # Why it is not valid (file_not_found, lines_out_of_range), or None.
    problem: str | None


class StoredMessage(BaseModel):
    id: uuid.UUID
    lens: Lens
    role: MessageRole
    content: str
    citations: list[TextCitation]
    created_at: datetime


# Events a lens use case emits while it answers (the router turns them into SSE).


class ConversationStarted(BaseModel):
    conversation_id: uuid.UUID


class TextDelta(BaseModel):
    text: str


class CitationsChecked(BaseModel):
    citations: list[TextCitation]


class AnswerDone(BaseModel):
    cached: bool = False
    message_id: uuid.UUID | None = None


class AnswerFailed(BaseModel):
    message: str


LensEvent = ConversationStarted | TextDelta | CitationsChecked | AnswerDone | AnswerFailed
