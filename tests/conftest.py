from typing import Optional

import pytest
from fastapi.testclient import TestClient
from requests import Response

from app.main import app
from app.services.base import TransfermarktBase
from tests.upstream import build_response, load_manifest


@pytest.fixture(scope="session")
def manifest() -> dict:
    """Recorded website fixtures index."""
    return load_manifest()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, manifest: dict) -> TestClient:
    """API client whose upstream requests are served from recorded fixtures; never touches the network."""

    def offline_make_request(self: TransfermarktBase, url: Optional[str] = None) -> Response:
        """Serve a website page from the recorded fixtures."""
        return build_response(url or self.URL, manifest)

    monkeypatch.setattr(TransfermarktBase, "make_request", offline_make_request)
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def live_client() -> TestClient:
    """API client that calls the real upstreams."""
    return TestClient(app, raise_server_exceptions=False)
