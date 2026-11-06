"""Plain data types produced by the extractors. No IO."""

from dataclasses import dataclass, field
from enum import StrEnum


class SkipReason(StrEnum):
    IGNORED_DIR = "ignored_dir"
    LOCKFILE = "lockfile"
    BINARY = "binary"
    MINIFIED = "minified"
    TOO_LARGE = "too_large"
    SECRET = "secret"
    UNSAFE_PATH = "unsafe_path"
    EMPTY = "empty"


@dataclass(frozen=True)
class ExtractedFile:
    path: str
    content: str


@dataclass(frozen=True)
class SkippedFile:
    path: str
    reason: SkipReason


@dataclass
class ExtractionResult:
    files: list[ExtractedFile] = field(default_factory=list)
    skipped: list[SkippedFile] = field(default_factory=list)


@dataclass(frozen=True)
class UploadLimits:
    max_unzipped_bytes: int
    max_files: int
