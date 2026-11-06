import pytest

from app.ingestion.errors import InvalidUpload, UploadTooLarge
from app.ingestion.extractors.zip import ZipExtractor
from app.ingestion.types import SkipReason, UploadLimits
from tests.fixtures.builders import make_zip

LIMITS = UploadLimits(max_unzipped_bytes=10 * 1024 * 1024, max_files=100)


def extract(files: dict[str, bytes | str], limits: UploadLimits = LIMITS):
    return ZipExtractor().extract("loja.zip", make_zip(files), limits)


def test_strips_github_root_folder_and_applies_filters() -> None:
    result = extract(
        {
            "loja-main/README.md": "# Loja",
            "loja-main/src/app.py": "print('oi')",
            "loja-main/.env": "SECRET=1",
            "loja-main/.env.example": "SECRET=",
            "loja-main/node_modules/x/index.js": "x",
            "loja-main/logo.bin": b"\x00\x01binary",
        }
    )

    assert sorted(f.path for f in result.files) == [".env.example", "README.md", "src/app.py"]
    reasons = {s.path: s.reason for s in result.skipped}
    assert reasons == {
        ".env": SkipReason.SECRET,
        "node_modules/x/index.js": SkipReason.IGNORED_DIR,
        "logo.bin": SkipReason.BINARY,
    }


def test_unsafe_paths_are_skipped() -> None:
    result = extract({"../../etc/passwd": "root", "/abs/file.py": "x", "ok.py": "y"})

    assert [f.path for f in result.files] == ["ok.py"]
    assert {s.reason for s in result.skipped} == {SkipReason.UNSAFE_PATH}


def test_real_unzipped_size_limit_is_enforced() -> None:
    limits = UploadLimits(max_unzipped_bytes=1000, max_files=100)

    with pytest.raises(UploadTooLarge, match="MAX_UNZIPPED_MB"):
        extract({"a.py": "a" * 600, "b.py": "b" * 600}, limits)


def test_file_count_limit_is_enforced() -> None:
    limits = UploadLimits(max_unzipped_bytes=LIMITS.max_unzipped_bytes, max_files=2)

    with pytest.raises(UploadTooLarge, match="MAX_FILES"):
        extract({"a.py": "a", "b.py": "b", "c.py": "c"}, limits)


def test_not_a_zip_is_a_friendly_error() -> None:
    with pytest.raises(InvalidUpload):
        ZipExtractor().extract("loja.zip", b"definitely not a zip", LIMITS)
