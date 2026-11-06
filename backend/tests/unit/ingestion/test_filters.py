import pytest

from app.ingestion.filters import is_binary, is_minified, path_priority, skip_reason_for_path
from app.ingestion.types import SkipReason


@pytest.mark.parametrize(
    ("path", "reason"),
    [
        ("node_modules/react/index.js", SkipReason.IGNORED_DIR),
        ("src/.git/config", SkipReason.IGNORED_DIR),
        ("package-lock.json", SkipReason.LOCKFILE),
        ("backend/uv.lock", SkipReason.LOCKFILE),
        (".env", SkipReason.SECRET),
        ("config/.env.production", SkipReason.SECRET),
        ("certs/server.pem", SkipReason.SECRET),
        ("public/logo.png", SkipReason.BINARY),
        ("assets/app.min.js", SkipReason.MINIFIED),
        (".env.example", None),
        ("src/services/payment.ts", None),
    ],
)
def test_skip_reason_for_path(path: str, reason: SkipReason | None) -> None:
    assert skip_reason_for_path(path) == reason


def test_content_checks_detect_binary_and_minified() -> None:
    assert is_binary(b"PK\x03\x04\x00\x00")
    assert not is_binary("olá".encode())
    assert is_minified("var a=1;" * 200)
    assert not is_minified("def main():\n    return 1\n")


def test_priority_reads_readme_routes_models_services_config_rest_tests() -> None:
    paths = [
        "tests/test_cart.py",
        "src/utils/format.ts",
        "package.json",
        "src/services/payment.ts",
        "src/models/order.ts",
        "src/routes/checkout.ts",
        "docs/README.md",
        "README.md",
    ]

    ordered = sorted(paths, key=path_priority)

    assert ordered == [
        "README.md",
        "docs/README.md",
        "src/routes/checkout.ts",
        "src/models/order.ts",
        "src/services/payment.ts",
        "package.json",
        "src/utils/format.ts",
        "tests/test_cart.py",
    ]
