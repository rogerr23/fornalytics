"""Zip extractor. Reads entries in memory (never to disk) and enforces upload limits."""

import io
import stat
import zipfile
from pathlib import PurePosixPath

from app.ingestion.errors import InvalidUpload, UploadTooLarge
from app.ingestion.filters import MAX_FILE_BYTES, is_binary, is_minified, skip_reason_for_path
from app.ingestion.text import decode_text
from app.ingestion.types import (
    ExtractedFile,
    ExtractionResult,
    SkippedFile,
    SkipReason,
    UploadLimits,
)

CHUNK_BYTES = 64 * 1024


class ZipExtractor:
    extensions = (".zip",)

    def extract(self, filename: str, data: bytes, limits: UploadLimits) -> ExtractionResult:
        try:
            archive = zipfile.ZipFile(io.BytesIO(data))
        except zipfile.BadZipFile as exc:
            raise InvalidUpload("O arquivo .zip está corrompido ou não é um zip.") from exc

        with archive:
            entries = [info for info in archive.infolist() if not info.is_dir()]
            if len(entries) > limits.max_files:
                raise UploadTooLarge(
                    f"O zip tem {len(entries)} arquivos; o limite é {limits.max_files} (MAX_FILES)."
                )
            prefix = _common_root([info.filename for info in entries])
            result = ExtractionResult()
            budget = _Budget(limits.max_unzipped_bytes)
            for info in entries:
                self._read_entry(archive, info, prefix, budget, result)
        return result

    def _read_entry(
        self,
        archive: zipfile.ZipFile,
        info: zipfile.ZipInfo,
        prefix: str,
        budget: "_Budget",
        result: ExtractionResult,
    ) -> None:
        raw_path = info.filename.replace("\\", "/")
        path = raw_path.removeprefix(prefix)
        if not _is_safe(raw_path) or _is_symlink(info):
            result.skipped.append(SkippedFile(path, SkipReason.UNSAFE_PATH))
            return
        if reason := skip_reason_for_path(path):
            result.skipped.append(SkippedFile(path, reason))
            return
        if info.flag_bits & 0x1:
            raise InvalidUpload("O zip está protegido por senha. Envie um zip sem senha.")
        if info.file_size > MAX_FILE_BYTES:
            result.skipped.append(SkippedFile(path, SkipReason.TOO_LARGE))
            return

        data = _read_limited(archive, info, budget)
        if data is None:
            result.skipped.append(SkippedFile(path, SkipReason.TOO_LARGE))
        elif is_binary(data):
            result.skipped.append(SkippedFile(path, SkipReason.BINARY))
        else:
            text = decode_text(data)
            if not text.strip():
                result.skipped.append(SkippedFile(path, SkipReason.EMPTY))
            elif is_minified(text):
                result.skipped.append(SkippedFile(path, SkipReason.MINIFIED))
            else:
                result.files.append(ExtractedFile(path, text))


class _Budget:
    """Counts real decompressed bytes. Headers can lie (zip bombs), so they are not trusted."""

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max_bytes
        self.used = 0

    def consume(self, size: int) -> None:
        self.used += size
        if self.used > self.max_bytes:
            limit_mb = self.max_bytes // (1024 * 1024)
            raise UploadTooLarge(
                f"O conteúdo descompactado passa de {limit_mb} MB (MAX_UNZIPPED_MB)."
            )


def _read_limited(archive: zipfile.ZipFile, info: zipfile.ZipInfo, budget: _Budget) -> bytes | None:
    """Read one entry; None if it turns out larger than the per-file limit."""
    buffer = bytearray()
    with archive.open(info) as entry:
        while chunk := entry.read(CHUNK_BYTES):
            budget.consume(len(chunk))
            buffer.extend(chunk)
            if len(buffer) > MAX_FILE_BYTES:
                return None
    return bytes(buffer)


def _is_safe(path: str) -> bool:
    pure = PurePosixPath(path)
    has_drive = len(path) > 1 and path[1] == ":"
    return not pure.is_absolute() and not has_drive and ".." not in pure.parts


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    return stat.S_ISLNK(info.external_attr >> 16)


def _common_root(names: list[str]) -> str:
    """'loja-main/' when every entry lives under one top folder (GitHub downloads), else ''."""
    normalized = [name.replace("\\", "/") for name in names]
    if not normalized or any("/" not in name for name in normalized):
        return ""
    roots = {name.split("/", 1)[0] for name in normalized}
    return f"{roots.pop()}/" if len(roots) == 1 else ""
