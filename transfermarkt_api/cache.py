"""Configuration for the SDK's per-client response caches."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class CacheConfig:
    """Successful response TTLs (seconds) and cache capacity."""

    ttl: float = 600
    reference_ttl: float = 86_400
    max_entries: int = 2_000

    def __post_init__(self) -> None:
        """Reject unusable cache settings before allocating resources."""
        if not isinstance(self.max_entries, int) or isinstance(self.max_entries, bool) or self.max_entries < 1:
            raise ValueError("max_entries must be a positive integer")
        if not all(isfinite(value) and value > 0 for value in (self.ttl, self.reference_ttl)):
            raise ValueError("cache TTLs must be finite and positive")
