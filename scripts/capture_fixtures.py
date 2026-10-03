"""
Record live Transfermarkt responses as offline test fixtures and refresh the response snapshots.

Every upstream request made while serving the cases in tests/cases.py is stored gzipped under
tests/fixtures/web/, and each API response is written to tests/snapshots/v3/.

Requires an IP that Transfermarkt's WAF does not challenge (cloud/datacenter IPs are usually blocked).

Usage: uv run python scripts/capture_fixtures.py
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
from tests.cases import CASES  # noqa: E402
from tests.snapshots import SNAPSHOTS_DIR, normalize  # noqa: E402
from tests.upstream import FIXTURES_DIR, MANIFEST_PATH, save_fixture  # noqa: E402


def parse_body(response: httpx2.Response) -> Any:
    """JSON body of a test client response, or its text when it is not JSON."""
    try:
        return response.json()
    except ValueError:
        return response.text


def main() -> None:
    """Serve every matching case against live upstreams, recording fixtures and snapshots."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest: dict = {}
    original_make_request = TransfermarktBase.make_request

    def recording_make_request(self: TransfermarktBase, url: Optional[str] = None) -> Response:
        """Fetch a website page for real and record it as a fixture."""
        target = url or self.URL
        response = original_make_request(self, url)
        if not response.content:
            raise RuntimeError(f"Empty response (likely WAF challenge) for {target}")
        save_fixture(target, response, manifest)
        return response

    TransfermarktBase.make_request = recording_make_request
    client = TestClient(app, raise_server_exceptions=False)

    for name, path in CASES:
        response = client.get(path)
        snapshot = {"status": response.status_code, "body": normalize(parse_body(response))}
        (SNAPSHOTS_DIR / f"{name}.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
        print(f"{response.status_code} {path}")

    MANIFEST_PATH.write_text(json.dumps(dict(sorted(manifest.items())), indent=2) + "\n")
    print(f"Recorded {len(manifest)} upstream responses")


if __name__ == "__main__":
    main()
