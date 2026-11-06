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


class FeatureStatus(StrEnum):
    """Where a feature stands between the idea and the code (Ideia × Código columns)."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    DOCUMENTED_ONLY = "documented_only"
    UNDOCUMENTED = "undocumented"


class Verdict(StrEnum):
    """Answer of "Isso o produto faz?"."""

    SIM = "sim"
    NAO = "nao"
    PARCIALMENTE = "parcialmente"
