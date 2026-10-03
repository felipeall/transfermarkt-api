"""
Recorded API responses.

- api/: expected output of the current code, refreshed by scripts/capture_fixtures.py.
- v3/: frozen output of the v3 HTML scraper (2026-10-03), the reference for comparing JSON-backed endpoints.
"""

from pathlib import Path
from typing import Any

SNAPSHOTS_DIR = Path(__file__).parent / "api"
BASELINE_V3_DIR = Path(__file__).parent / "v3"
VOLATILE_KEYS = {"updatedAt"}


def normalize(data: Any) -> Any:
    """Drop fields that change on every request, so snapshots compare deterministically."""
    if isinstance(data, dict):
        return {k: normalize(v) for k, v in data.items() if k not in VOLATILE_KEYS}
    if isinstance(data, list):
        return [normalize(v) for v in data]
    return data
