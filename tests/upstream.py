"""Offline upstream fixtures: recorded Transfermarkt responses keyed by URL."""

import gzip
import hashlib
import json
import re
from pathlib import Path

from requests import Response

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "web"
MANIFEST_PATH = FIXTURES_DIR / "manifest.json"


def fixture_name(url: str) -> str:
    """File name of the fixture for a URL: readable slug plus a short hash."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", url.split("://", 1)[-1]).strip("-")[:80]
    digest = hashlib.sha1(url.encode()).hexdigest()[:10]
    return f"{slug}-{digest}.gz"


def load_manifest() -> dict:
    """Load the fixture index (URL -> file, status, content type)."""
    if not MANIFEST_PATH.exists():
        return {}
    return json.loads(MANIFEST_PATH.read_text())


def save_fixture(url: str, response: Response, manifest: dict) -> None:
    """Store a response body gzipped and add it to the manifest."""
    name = fixture_name(url)
    (FIXTURES_DIR / name).write_bytes(gzip.compress(response.content, mtime=0))
    manifest[url] = {
        "file": name,
        "status": response.status_code,
        "contentType": response.headers.get("Content-Type"),
    }


def build_response(url: str, manifest: dict) -> Response:
    """A `requests.Response` replaying the recorded fixture for a URL."""
    entry = manifest.get(url)
    if entry is None:
        raise LookupError(f"No recorded fixture for {url}. Run scripts/capture_fixtures.py.")

    response = Response()
    response.url = url
    response.status_code = entry["status"]
    response.headers["Content-Type"] = entry["contentType"] or ""
    response._content = gzip.decompress((FIXTURES_DIR / entry["file"]).read_bytes())
    return response
