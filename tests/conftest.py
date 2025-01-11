import json
from pathlib import Path

import pytest


@pytest.fixture
def load_test_data() -> callable:
    def _load_test_data(file_name: str) -> dict:
        file_path = Path(__file__).parent / "data" / f"{file_name}.json"

        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    return _load_test_data
