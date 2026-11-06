"""Fixed vocabularies shared by the whole backend. Stored as text in the database."""

from enum import StrEnum


class Lens(StrEnum):
    CLIENTE = "cliente"
    NAO_TECNICO = "nao_tecnico"
    TECNICO = "tecnico"


class ProjectStatus(StrEnum):
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class SourceType(StrEnum):
    CODE = "code"
    IDEA_DOC = "idea_doc"
    TRANSCRIPT = "transcript"
    TEXT = "text"


class CacheKind(StrEnum):
    OVERVIEW = "overview"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
