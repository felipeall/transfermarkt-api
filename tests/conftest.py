from collections.abc import Iterator
from typing import Optional

import pytest
from fastapi.testclient import TestClient
from requests import Response

from app.main import app
from app.services.base import TransfermarktBase
from app.tfmkt import TfmktClient, get_tfmkt
from tests.upstream import FixtureStore, tfmkt_transport, web_response


@pytest.fixture(scope="session")
def web_store() -> FixtureStore:
    """Recorded website pages."""
    return FixtureStore("web")


@pytest.fixture(scope="session")
def tfmkt_store() -> FixtureStore:
    """Recorded tfmkt responses."""
    return FixtureStore("tfmkt")


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, web_store: FixtureStore, tfmkt_store: FixtureStore) -> Iterator[TestClient]:
    """API client whose upstream requests are served from recorded fixtures; never touches the network."""

    def offline_make_request(self: TransfermarktBase, url: Optional[str] = None) -> Response:
        """Serve a website page from the recorded fixtures."""
        return web_response(web_store, url or self.URL)

    monkeypatch.setattr(TransfermarktBase, "make_request", offline_make_request)
    tfmkt = TfmktClient(transport=tfmkt_transport(tfmkt_store))
    app.dependency_overrides[get_tfmkt] = lambda: tfmkt
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def live_client() -> Iterator[TestClient]:
    """API client that calls the real upstreams."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
