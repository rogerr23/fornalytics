"""What the lenses produce: streamed text, text citations and chat messages."""

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import FeatureStatus, Lens, MessageRole, Verdict
from app.domain.product_base import Evidence


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


# Side by side: one model call answers in the three lenses (structured output schema).


class CompareDraft(BaseModel):
    cliente: str
    nao_tecnico: str
    tecnico: str


class LensAnswer(BaseModel):
    lens: Lens
    text: str
    citations: list[TextCitation]


class CompareResult(BaseModel):
    question: str
    answers: list[LensAnswer]


# "Isso o produto faz?": the verdict always agrees with the product base.


class DoesItDraft(BaseModel):
    """Structured output schema. `feature_name` is "" when no base feature answers it."""

    verdict: Verdict
    feature_name: str
    justification: str
    evidence: list[Evidence]


class MatchedFeature(BaseModel):
    name: str
    status: FeatureStatus


class DoesItResult(BaseModel):
    question: str
    verdict: Verdict
    feature: MatchedFeature | None
    justification: str
    evidence: list[Evidence]
    # True when the backend changed the model's verdict to agree with the base.
    adjusted: bool
