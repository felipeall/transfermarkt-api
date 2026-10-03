"""
Record live tfmkt responses as offline test fixtures and refresh the response snapshots.

Every upstream request made while serving the cases in tests/cases.py is stored gzipped under tests/fixtures/tfmkt/,
and each API response is written to tests/snapshots/api/. Existing fixtures are kept; recorded URLs are overwritten.
Delete tests/fixtures/tfmkt/ first to drop responses no longer used.

Usage: uv run python scripts/capture_fixtures.py [case-name-substring ...]
"""

import json
import sys
from pathlib import Path
from typing import Any

import httpx2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
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
    tfmkt_store = FixtureStore("tfmkt")
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

    tfmkt_store.write_manifest()
    print(f"Fixtures: {len(tfmkt_store.manifest)} tfmkt responses")


if __name__ == "__main__":
    main(sys.argv[1:])
