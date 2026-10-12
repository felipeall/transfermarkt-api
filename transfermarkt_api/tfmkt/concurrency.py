"""Ordered fan-out with cleanup before failures leave the SDK."""

import asyncio
from collections.abc import Awaitable
from typing import Any


async def gather(*awaitables: Awaitable[Any]) -> list[Any]:
    """Return results in input order, cancelling and awaiting siblings on any failure."""
    tasks = [asyncio.ensure_future(awaitable) for awaitable in awaitables]
    try:
        return await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
