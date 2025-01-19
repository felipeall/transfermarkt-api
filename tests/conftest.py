import json
from pathlib import Path

import pytest
from pydantic import BaseModel


@pytest.fixture
def load_test_data() -> callable:
    """Load test data from the `tests/data` directory."""

    def _load_test_data(file_name: str) -> dict:
        file_path = Path(__file__).parent / "data" / f"{file_name}.json"

        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    return _load_test_data


@pytest.fixture(autouse=True)
def override_pydantic_eq():
    """Override Pydantic's __eq__ method to ignore the `updated_at` field."""
    original_eq = BaseModel.__eq__

    def custom_eq(self, other):
        if not isinstance(other, self.__class__):
            return False
        self_dict = self.model_dump()
        other_dict = other.model_dump()
        self_dict.pop("updated_at", None)
        other_dict.pop("updated_at", None)
        return self_dict == other_dict

    BaseModel.__eq__ = custom_eq
    yield
    BaseModel.__eq__ = original_eq
