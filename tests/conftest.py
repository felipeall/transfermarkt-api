from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_tfmkt
from app.main import app
from tests.upstream import FixtureStore, tfmkt_transport
from transfermarkt_api import Transfermarkt


@pytest.fixture(scope="session")
def tfmkt_store() -> FixtureStore:
    """Recorded tfmkt responses."""
    return FixtureStore("tfmkt")


@pytest.fixture
def client(tfmkt_store: FixtureStore) -> Iterator[TestClient]:
    """API client whose upstream requests are served from recorded fixtures; never touches the network."""
    tfmkt = Transfermarkt(transport=tfmkt_transport(tfmkt_store))
    app.dependency_overrides[get_tfmkt] = lambda: tfmkt
    with TestClient(app, raise_server_exceptions=False) as test_client:
        try:
            yield test_client
        finally:
            test_client.portal.call(tfmkt.aclose)
            app.dependency_overrides.clear()


@pytest.fixture
def live_client() -> Iterator[TestClient]:
    """API client that calls the real upstreams."""
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
