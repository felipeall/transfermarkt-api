"""Offline upstream fixtures: recorded tfmkt responses keyed by URL."""

import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Optional

import httpx

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class FixtureStore:
    """Gzipped response bodies in `directory`, indexed by URL in `manifest.json`."""

    def __init__(self, name: str) -> None:
        """Open the fixture directory `tests/fixtures/<name>` and load its manifest."""
        self.directory = FIXTURES_DIR / name
        self.manifest_path = self.directory / "manifest.json"
        self.manifest: dict = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}
        self.pending: dict[str, tuple[dict, bytes]] = {}

    @staticmethod
    def file_name(url: str) -> str:
        """File name of the fixture for a URL: readable slug plus a short hash."""
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", url.split("://", 1)[-1]).strip("-")[:80]
        digest = hashlib.sha1(url.encode()).hexdigest()[:10]
        return f"{slug}-{digest}.gz"

    def save(self, url: str, status: int, content_type: Optional[str], content: bytes) -> None:
        """Stage a response for `commit`. Nothing is written to disk until then."""
        entry = {"file": self.file_name(url), "status": status, "contentType": content_type}
        self.pending[url] = (entry, content)

    def commit(self) -> None:
        """Write the staged responses gzipped and update `manifest.json`, sorted by URL."""
        self.directory.mkdir(parents=True, exist_ok=True)
        for url, (entry, content) in self.pending.items():
            (self.directory / entry["file"]).write_bytes(gzip.compress(content, mtime=0))
            self.manifest[url] = entry
        self.pending.clear()
        self.manifest_path.write_text(json.dumps(dict(sorted(self.manifest.items())), indent=2) + "\n")

    def load(self, url: str) -> tuple[int, str, bytes]:
        """Status, content type and body recorded for a URL."""
        entry = self.manifest.get(url)
        if entry is None:
            raise LookupError(f"No recorded fixture for {url}. Run scripts/capture_fixtures.py.")
        content = gzip.decompress((self.directory / entry["file"]).read_bytes())
        return entry["status"], entry["contentType"] or "", content


def tfmkt_transport(store: FixtureStore) -> httpx.MockTransport:
    """An httpx transport replaying recorded tfmkt responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        """Serve a request from the recorded responses."""
        status, content_type, content = store.load(str(request.url))
        return httpx.Response(status, headers={"Content-Type": content_type}, content=content)

    return httpx.MockTransport(handler)


class RecordingTransport(httpx.AsyncBaseTransport):
    """Forwards requests to the real upstream and stores every response in `store`."""

    def __init__(self, store: FixtureStore) -> None:
        """Forward to a real HTTP transport and record into `store`."""
        self.store = store
        self.transport = httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """Send the request upstream and record the response."""
        response = await self.transport.handle_async_request(request)
        content = await response.aread()
        self.store.save(str(request.url), response.status_code, response.headers.get("Content-Type"), content)
        # body is already decoded; drop headers that describe the encoded form
        dropped = ("content-encoding", "content-length")
        headers = [(k, v) for k, v in response.headers.items() if k.lower() not in dropped]
        return httpx.Response(response.status_code, headers=headers, content=content)
