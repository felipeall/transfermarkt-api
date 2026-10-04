"""Fixture recording: nothing reaches disk until the capture commits it."""

from pathlib import Path

import pytest

from scripts.capture_fixtures import is_failure
from tests import upstream
from tests.upstream import FixtureStore


def test_saved_responses_are_written_only_on_commit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Staged responses leave existing fixtures untouched until `commit`, then replay as recorded."""
    monkeypatch.setattr(upstream, "FIXTURES_DIR", tmp_path)
    store = FixtureStore("tfmkt")

    store.save("https://tfmkt.test/player/1", 200, "application/json", b'{"ok": true}')

    assert not (tmp_path / "tfmkt").exists()

    store.commit()

    assert FixtureStore("tfmkt").load("https://tfmkt.test/player/1") == (200, "application/json", b'{"ok": true}')


@pytest.mark.parametrize(("status", "failed"), [(200, False), (404, False), (501, False), (500, True), (503, True)])
def test_capture_failures_are_server_errors_except_501(status: int, failed: bool) -> None:
    """Server errors stop the capture; 501 is the intended answer of unsupported endpoints."""
    assert is_failure(status) is failed
