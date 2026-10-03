from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.tfmkt import TfmktClient, get_tfmkt
from tests.upstream import FixtureStore, tfmkt_transport


@pytest.fixture(scope="session")
def tfmkt_store() -> FixtureStore:
    """Recorded tfmkt responses."""
    return FixtureStore("tfmkt")


@pytest.fixture
def client(tfmkt_store: FixtureStore) -> Iterator[TestClient]:
    """API client whose upstream requests are served from recorded fixtures; never touches the network."""
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
