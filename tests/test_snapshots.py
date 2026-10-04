"""Regression net: every endpoint, served from recorded upstream pages, must reproduce its recorded response."""

import json
from typing import Any

import httpx2
import pytest
from fastapi.testclient import TestClient

from tests.cases import CASES
from tests.snapshots import SNAPSHOTS_DIR, normalize


def parse_body(response: httpx2.Response) -> Any:
    """JSON body of a test client response, or its text when it is not JSON."""
    try:
        return response.json()
    except ValueError:
        return response.text


@pytest.mark.parametrize("name,path", CASES, ids=[name for name, _ in CASES])
def test_response_matches_snapshot(client: TestClient, name: str, path: str) -> None:
    """Every endpoint, served from recorded upstream data, reproduces its recorded response."""
    expected = json.loads((SNAPSHOTS_DIR / f"{name}.json").read_text())

    response = client.get(path)
    body = parse_body(response)

    if response.status_code == 200:
        assert "updatedAt" in body  # dropped by normalize(), so checked here
    assert {"status": response.status_code, "body": normalize(body)} == expected
