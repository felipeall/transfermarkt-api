"""
Record live tfmkt responses as offline test fixtures and refresh the response snapshots.

Every upstream request made while serving the cases in tests/cases.py is stored gzipped under tests/fixtures/tfmkt/,
and each API response is written to tests/snapshots/api/. Existing fixtures are kept; recorded URLs are overwritten.
Delete tests/fixtures/tfmkt/ first to drop responses no longer used.

Nothing is written if any case fails with a server error (5xx other than 501 Not Implemented), so a broken upstream
or a bug never becomes the expected response.

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


def is_failure(status: int) -> bool:
    """Whether a response status means the case failed. 501 is an intended response for unsupported endpoints."""
    return status >= 500 and status != 501


def main(filters: list[str]) -> int:
    """Serve every matching case against live upstreams, then record fixtures and snapshots if none failed."""
    tfmkt_store = FixtureStore("tfmkt")
    tfmkt = TfmktClient(transport=RecordingTransport(tfmkt_store))
    app.dependency_overrides[get_tfmkt] = lambda: tfmkt

    snapshots = {}
    with TestClient(app, raise_server_exceptions=False) as client:
        for name, path in CASES:
            if filters and not any(f in name for f in filters):
                continue
            response = client.get(path)
            snapshots[name] = {"status": response.status_code, "body": normalize(parse_body(response))}
            print(f"{response.status_code} {path}")

    failed = [name for name, snapshot in snapshots.items() if is_failure(snapshot["status"])]
    if failed:
        print(f"Nothing written: {len(failed)} case(s) failed: {', '.join(failed)}", file=sys.stderr)
        return 1

    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    for name, snapshot in snapshots.items():
        (SNAPSHOTS_DIR / f"{name}.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    tfmkt_store.commit()
    print(f"Fixtures: {len(tfmkt_store.manifest)} tfmkt responses")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
