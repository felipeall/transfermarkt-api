"""
Live smoke tests against real Transfermarkt upstreams. Deselected by default; run with `uv run pytest -m live`.

A failure here means upstream access or markup changed, not necessarily a code regression.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.live


@pytest.mark.parametrize(
    "path",
    [
        "/players/28003/profile",
        "/players/28003/stats",
        "/players/search/messi",
        "/clubs/131/profile",
        "/clubs/?country_id=189",
        "/countries/",
        "/clubs/131/players",
        "/competitions/GB1/clubs",
        "/competitions/GB1/table",
        "/players/28003/achievements",
        "/coaches/5672/profile",
    ],
)
def test_endpoint_responds(live_client: TestClient, path: str) -> None:
    """Endpoint answers 200 against the real upstream."""
    response = live_client.get(path)

    assert response.status_code == 200, response.text


def test_unknown_player_is_not_found(live_client: TestClient) -> None:
    """Unknown player IDs answer 404."""
    assert live_client.get("/players/0/profile").status_code == 404
