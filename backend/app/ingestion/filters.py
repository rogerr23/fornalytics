"""What to ignore and what to read first. Pure functions over paths and content."""

from pathlib import PurePosixPath

from app.ingestion.types import SkipReason

MAX_FILE_BYTES = 200 * 1024

IGNORED_DIRS = frozenset(
    {
        "node_modules",
        ".git",
        "dist",
        "build",
        ".next",
        "venv",
        ".venv",
        "__pycache__",
        ".idea",
        ".vscode",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".turbo",
        "coverage",
    }
)

LOCKFILES = frozenset(
    {
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        "uv.lock",
        "poetry.lock",
        "pipfile.lock",
        "cargo.lock",
        "composer.lock",
        "gemfile.lock",
        "go.sum",
    }
)

BINARY_EXTENSIONS = frozenset(
    {
        # images
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp", ".svg", ".tiff", ".psd",
        # fonts
        ".woff", ".woff2", ".ttf", ".otf", ".eot",
        # media
        ".mp3", ".mp4", ".wav", ".mov", ".avi", ".webm", ".ogg",
        # archives and documents
        ".zip", ".tar", ".gz", ".rar", ".7z", ".pdf", ".docx", ".xlsx", ".pptx",
        # compiled and data
        ".exe", ".dll", ".so", ".dylib", ".bin", ".class", ".jar", ".pyc", ".o", ".a",
        ".wasm", ".sqlite", ".db",
    }
)  # fmt: skip

SECRET_EXTENSIONS = frozenset({".pem", ".key", ".p12", ".pfx"})
SAFE_ENV_FILES = frozenset({".env.example", ".env.sample", ".env.template"})

# A file whose average line is this long is generated/minified, not hand-written.
MINIFIED_AVG_LINE_LENGTH = 500


def skip_reason_for_path(path: str) -> SkipReason | None:
    """Decide from the path alone (before reading the content)."""
    parts = PurePosixPath(path).parts
    name = parts[-1].lower()
    suffix = PurePosixPath(name).suffix
    if any(part in IGNORED_DIRS for part in parts[:-1]):
        return SkipReason.IGNORED_DIR
    if name in LOCKFILES:
        return SkipReason.LOCKFILE
    if (name == ".env" or name.startswith(".env.")) and name not in SAFE_ENV_FILES:
        return SkipReason.SECRET
    if suffix in SECRET_EXTENSIONS:
        return SkipReason.SECRET
    if suffix in BINARY_EXTENSIONS:
        return SkipReason.BINARY
    if name.endswith((".min.js", ".min.css", ".map")):
        return SkipReason.MINIFIED
    return None


def is_binary(data: bytes) -> bool:
    return b"\x00" in data[:8192]


def is_minified(text: str) -> bool:
    lines = text.splitlines() or [""]
    return len(text) / len(lines) > MINIFIED_AVG_LINE_LENGTH


# Reading order: lower group first. Matched against path segments and the file name.
_ROUTE_HINTS = ("route", "router", "controller", "endpoint", "handler", "api")
_MODEL_HINTS = ("model", "schema", "entity", "entities", "migration", "prisma")
_SERVICE_HINTS = ("service", "usecase", "use_case", "domain")
_CONFIG_NAMES = frozenset(
    {
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "dockerfile",
        "docker-compose.yml",
        "tsconfig.json",
        ".env.example",
        "settings.py",
        "config.py",
    }
)
_TEST_HINTS = ("test", "tests", "spec", "__tests__")


def path_priority(path: str) -> tuple[int, int, str]:
    """Sort key (group, depth, path).

    Groups: README < routes < models < services < config < rest < tests.
    """
    pure = PurePosixPath(path.lower())
    tokens = [*pure.parts[:-1], pure.stem]
    depth = len(pure.parts)

    def has(hints: tuple[str, ...]) -> bool:
        return any(hint in token for token in tokens for hint in hints)

    if pure.name.startswith("readme"):
        group = 0
    elif has(_TEST_HINTS):
        group = 6
    elif has(_ROUTE_HINTS):
        group = 1
    elif has(_MODEL_HINTS):
        group = 2
    elif has(_SERVICE_HINTS):
        group = 3
    elif pure.name in _CONFIG_NAMES or "config" in pure.stem or "settings" in pure.stem:
        group = 4
    else:
        group = 5
    return (group, depth, path)
