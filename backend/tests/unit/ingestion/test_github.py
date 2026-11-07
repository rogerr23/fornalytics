import httpx
import pytest

from app.ingestion.errors import InvalidUpload, SourceUnavailable, UploadTooLarge
from app.ingestion.extractors.zip import ZipExtractor
from app.ingestion.remote.github import GitHubRepo, download_repo_zip, parse_github_url
from app.ingestion.types import UploadLimits
from tests.fixtures.builders import make_zip


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/pallets/flask", GitHubRepo("pallets", "flask")),
        ("github.com/pallets/flask/", GitHubRepo("pallets", "flask")),
        ("http://www.github.com/pallets/flask.git", GitHubRepo("pallets", "flask")),
        ("  https://GitHub.com/pallets/flask?tab=readme#x ", GitHubRepo("pallets", "flask")),
        ("https://github.com/pallets/flask/tree/3.1.x", GitHubRepo("pallets", "flask", "3.1.x")),
    ],
)
def test_accepted_links(url: str, expected: GitHubRepo) -> None:
    assert parse_github_url(url) == expected


@pytest.mark.parametrize(
    ("url", "message"),
    [
        ("https://gitlab.com/a/b", "Só links do GitHub"),
        ("https://github.com.evil.com/a/b", "Só links do GitHub"),
        ("https://evil.com/github.com/a/b", "Só links do GitHub"),
        ("https://github.com/pallets", "Faltou o nome"),
        ("https://github.com/-bad/flask", "inválido"),
        ("https://github.com/pallets/..", "inválido"),
        ("https://github.com/pallets/flask/issues", "não de uma página"),
        ("https://github.com/pallets/flask/tree/main/src", "subpasta"),
        ("https://github.com/pallets/flask/tree/a..b", "branch inválido"),
    ],
)
def test_refused_links(url: str, message: str) -> None:
    with pytest.raises(InvalidUpload, match=message):
        parse_github_url(url)


def test_archive_url_is_always_built_on_github_host() -> None:
    assert GitHubRepo("pallets", "flask").archive_url == (
        "https://codeload.github.com/pallets/flask/zip/HEAD"
    )
    assert GitHubRepo("pallets", "flask", "dev").label == "github.com/pallets/flask@dev"


def client_returning(status: int, body: bytes = b"") -> tuple[httpx.AsyncClient, list[str]]:
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(status, content=body)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler)), requested


async def test_download_returns_a_zip_the_extractor_reads() -> None:
    archive = make_zip({"flask-main/README.md": "# Flask", "flask-main/src/app.py": "x = 1"})
    client, requested = client_returning(200, archive)

    data = await download_repo_zip(client, GitHubRepo("pallets", "flask"), max_mb=1)

    assert requested == ["https://codeload.github.com/pallets/flask/zip/HEAD"]
    limits = UploadLimits(max_unzipped_bytes=1024 * 1024, max_files=10)
    result = ZipExtractor().extract("flask.zip", data, limits)
    assert sorted(f.path for f in result.files) == ["README.md", "src/app.py"]


async def test_download_stops_past_max_upload_mb() -> None:
    client, _ = client_returning(200, b"x" * (1024 * 1024 + 1))

    with pytest.raises(UploadTooLarge, match="MAX_UPLOAD_MB"):
        await download_repo_zip(client, GitHubRepo("a", "b"), max_mb=1)


async def test_missing_or_private_repo_is_a_friendly_error() -> None:
    client, _ = client_returning(404)

    with pytest.raises(InvalidUpload, match="privado"):
        await download_repo_zip(client, GitHubRepo("a", "b"), max_mb=1)


@pytest.mark.parametrize("status", [302, 403, 429, 503])
async def test_other_statuses_are_unavailable(status: int) -> None:
    client, _ = client_returning(status)

    with pytest.raises(SourceUnavailable):
        await download_repo_zip(client, GitHubRepo("a", "b"), max_mb=1)


async def test_network_failure_is_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    with pytest.raises(SourceUnavailable, match="internet"):
        await download_repo_zip(client, GitHubRepo("a", "b"), max_mb=1)
