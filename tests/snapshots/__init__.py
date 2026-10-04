"""Recorded API responses. v3/ holds the HTML-scraper output, kept as the baseline for the JSON migration."""

from pathlib import Path
from typing import Any

SNAPSHOTS_DIR = Path(__file__).parent / "v3"
VOLATILE_KEYS = {"updatedAt"}


def normalize(data: Any) -> Any:
    """Drop fields that change on every request, so snapshots compare deterministically."""
    if isinstance(data, dict):
        return {k: normalize(v) for k, v in data.items() if k not in VOLATILE_KEYS}
    if isinstance(data, list):
        return [normalize(v) for v in data]
    return data
