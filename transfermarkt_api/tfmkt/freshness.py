"""
Track when the upstream data behind a response was fetched, so `updatedAt` stays truthful when served from cache.

`fetch_scope()` starts a per-call record before assembly and model validation. The client reports
each response it uses, fresh or cached, and `data_fetched_at()` returns the oldest fetch time. The record is a
mutable list shared through a context variable, so fetches made inside `asyncio.gather` child tasks are seen by
the request.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Optional

_fetch_times: ContextVar[Optional[list[datetime]]] = ContextVar("tfmkt_fetch_times", default=None)


@contextmanager
def fetch_scope() -> Iterator[None]:
    """Isolate one assembly operation, restoring the calling context even on failure."""
    token = _fetch_times.set([])
    try:
        yield
    finally:
        _fetch_times.reset(token)


def record_fetch(fetched_at: datetime) -> None:
    """Record when a response used by the current request was fetched from upstream."""
    fetch_times = _fetch_times.get()
    if fetch_times is not None:
        fetch_times.append(fetched_at)


def data_fetched_at() -> datetime:
    """Oldest fetch time recorded for the current request, or now when nothing was fetched."""
    return min(_fetch_times.get() or [], default=None) or datetime.now(UTC).replace(tzinfo=None)
