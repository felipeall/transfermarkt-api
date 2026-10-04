"""Per-client rate limiting across the whole API, kept in memory."""

import math
import time

from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter


class RateLimiter:
    """One moving-window budget per client key, shared by every route."""

    def __init__(self, limit: str, enabled: bool) -> None:
        """Parse `limit` (e.g. "2/3seconds", see the `limits` string notation) and start with empty counters."""
        self.limit = parse(limit)
        self.enabled = enabled
        self.storage = MemoryStorage()
        self.strategy = MovingWindowRateLimiter(self.storage)

    def hit(self, key: str) -> bool:
        """Count a request from `key`; False when it is over the limit."""
        return self.strategy.hit(self.limit, key)

    def retry_after(self, key: str) -> int:
        """Whole seconds until `key` can make another request."""
        reset_time = self.strategy.get_window_stats(self.limit, key).reset_time
        return max(1, math.ceil(reset_time - time.time()))

    def reset(self) -> None:
        """Forget all counters."""
        self.storage.reset()
