"""
Record live upstream responses as offline test fixtures and refresh the response snapshots.

Every upstream request made while serving the cases in tests/cases.py is stored gzipped: website pages under
tests/fixtures/web/, tfmkt JSON under tests/fixtures/tfmkt/. Each API response is written to tests/snapshots/api/.
Existing fixtures are kept; recorded URLs are overwritten.

Website pages need an IP that Transfermarkt's WAF does not block (cloud/datacenter IPs usually are).

Usage: uv run python scripts/capture_fixtures.py [case-name-substring ...]
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional

import httpx2
from requests import Response

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.base import TransfermarktBase  # noqa: E402
from app.tfmkt import TfmktClient, get_tfmkt  # noqa: E402
from tests.cases import CASES  # noqa: E402
from tests.snapshots import SNAPSHOTS_DIR, normalize  # noqa: E402
from tests.upstream import FixtureStore, RecordingTransport  # noqa: E402


def parse_body(response: httpx2.Response) -> Any:
    """JSON body of a test client response, or its text when it is not JSON."""
    try:
        return response.json()
    except ValueError:
        return response.text


def main(filters: list[str]) -> None:
    """Serve every matching case against live upstreams, recording fixtures and snapshots."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    web_store = FixtureStore("web")
    tfmkt_store = FixtureStore("tfmkt")
    original_make_request = TransfermarktBase.make_request

    def recording_make_request(self: TransfermarktBase, url: Optional[str] = None) -> Response:
        """Fetch a website page for real and record it as a fixture."""
        target = url or self.URL
        response = original_make_request(self, url)
        if not response.content:
            raise RuntimeError(f"Empty response (likely WAF challenge) for {target}")
        web_store.save(target, response.status_code, response.headers.get("Content-Type"), response.content)
        return response

    TransfermarktBase.make_request = recording_make_request
    tfmkt = TfmktClient(transport=RecordingTransport(tfmkt_store))
    app.dependency_overrides[get_tfmkt] = lambda: tfmkt

    with TestClient(app, raise_server_exceptions=False) as client:
        for name, path in CASES:
            if filters and not any(f in name for f in filters):
                continue
            response = client.get(path)
            snapshot = {"status": response.status_code, "body": normalize(parse_body(response))}
            (SNAPSHOTS_DIR / f"{name}.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
            print(f"{response.status_code} {path}")

    web_store.write_manifest()
    tfmkt_store.write_manifest()
    print(f"Fixtures: {len(web_store.manifest)} web, {len(tfmkt_store.manifest)} tfmkt")


if __name__ == "__main__":
    main(sys.argv[1:])
