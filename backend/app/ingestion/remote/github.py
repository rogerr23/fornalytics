"""Public GitHub repository by link: parse the URL and download the repository as a zip.

Only owner, repository and branch are taken from the user's link. The download URL is always
built here, on GitHub's fixed archive host, so a link can never make the server fetch anything
else. No redirects are followed.
"""

import asyncio
import re
from dataclasses import dataclass

import httpx

from app.ingestion.errors import InvalidUpload, SourceUnavailable, UploadTooLarge

ARCHIVE_HOST = "https://codeload.github.com"
DOWNLOAD_TIMEOUT_SECONDS = 120
HTTP_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

_HOSTS = frozenset({"github.com", "www.github.com"})
_OWNER = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
_REPO = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
_REF = re.compile(r"^[A-Za-z0-9._-]{1,100}$")
_SCHEME = re.compile(r"^https?://", re.IGNORECASE)

EXPECTED_FORMAT = "Use um link como https://github.com/dono/repositorio."


@dataclass(frozen=True)
class GitHubRepo:
    owner: str
    name: str
    ref: str | None = None

    @property
    def label(self) -> str:
        """Shown as the source's name (fits the 255-character filename column)."""
        base = f"github.com/{self.owner}/{self.name}"
        return f"{base}@{self.ref}" if self.ref else base

    @property
    def archive_url(self) -> str:
        # HEAD = the repository's default branch.
        return f"{ARCHIVE_HOST}/{self.owner}/{self.name}/zip/{self.ref or 'HEAD'}"


def parse_github_url(url: str) -> GitHubRepo:
    """Accepts github.com/owner/repo, with or without https://, .git or /tree/branch."""
    text = _SCHEME.sub("", url.strip())
    text = re.split(r"[?#]", text, maxsplit=1)[0]
    host, _, path = text.partition("/")
    if host.lower() not in _HOSTS:
        raise InvalidUpload(f"Só links do GitHub são aceitos. {EXPECTED_FORMAT}")

    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        raise InvalidUpload(f"Faltou o nome do repositório. {EXPECTED_FORMAT}")
    owner, name = parts[0], parts[1].removesuffix(".git")
    if not _OWNER.match(owner) or not _REPO.match(name) or name in {".", ".."}:
        raise InvalidUpload(f"Link do GitHub inválido. {EXPECTED_FORMAT}")

    rest = parts[2:]
    if not rest:
        return GitHubRepo(owner, name)
    if rest[0] != "tree" or len(rest) == 1:
        raise InvalidUpload(f"Use o link do repositório, não de uma página dele. {EXPECTED_FORMAT}")
    if len(rest) > 2:
        raise InvalidUpload(
            "Links de subpasta (ou de branch com '/' no nome) ainda não são aceitos. "
            "Use o link do repositório ou do branch."
        )
    ref = rest[1]
    if not _REF.match(ref) or ".." in ref:
        raise InvalidUpload(f"Nome de branch inválido. {EXPECTED_FORMAT}")
    return GitHubRepo(owner, name, ref)


async def download_repo_zip(client: httpx.AsyncClient, repo: GitHubRepo, max_mb: int) -> bytes:
    """Stream the archive into memory, stopping as soon as it passes MAX_UPLOAD_MB."""
    try:
        async with asyncio.timeout(DOWNLOAD_TIMEOUT_SECONDS):
            return await _download(client, repo, max_mb)
    except (TimeoutError, httpx.TimeoutException) as exc:
        raise SourceUnavailable(
            "O GitHub demorou demais para responder. Tente de novo ou envie o .zip."
        ) from exc
    except httpx.HTTPError as exc:
        raise SourceUnavailable(
            "Não foi possível falar com o GitHub. Confira a internet e tente de novo, "
            "ou envie o .zip."
        ) from exc


async def _download(client: httpx.AsyncClient, repo: GitHubRepo, max_mb: int) -> bytes:
    max_bytes = max_mb * 1024 * 1024
    async with client.stream(
        "GET", repo.archive_url, follow_redirects=False, timeout=HTTP_TIMEOUT
    ) as response:
        _check_status(response, repo)
        buffer = bytearray()
        async for chunk in response.aiter_bytes():
            buffer.extend(chunk)
            if len(buffer) > max_bytes:
                raise UploadTooLarge(
                    f"O repositório passa de {max_mb} MB (MAX_UPLOAD_MB). "
                    "Envie um .zip só com as pastas importantes."
                )
    return bytes(buffer)


def _check_status(response: httpx.Response, repo: GitHubRepo) -> None:
    if response.status_code == 200:
        return
    if response.status_code == 404:
        what = f"o branch '{repo.ref}'" if repo.ref else "o repositório"
        raise InvalidUpload(
            f"Não encontrei {what} no GitHub, ou o repositório é privado. "
            "Só repositórios públicos são aceitos."
        )
    if response.status_code in {403, 429}:
        raise SourceUnavailable(
            "O GitHub limitou os downloads por agora. Espere alguns minutos ou envie o .zip."
        )
    raise SourceUnavailable(
        f"O GitHub respondeu com erro ({response.status_code}). Tente de novo ou envie o .zip."
    )
