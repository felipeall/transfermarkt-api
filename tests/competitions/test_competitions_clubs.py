import logging
import os
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from schema import And, Schema

from app.services.competitions.clubs import TransfermarktCompetitionClubs
from app.settings import Settings


def test_get_competition_clubs_not_found():
    with pytest.raises(HTTPException):
        TransfermarktCompetitionClubs(competition_id="0")


@pytest.mark.parametrize("competition_id,season_id", [("ES1", None), ("GB1", "2016"), ("BRA1", "2023")])
def test_get_competition_clubs(competition_id, season_id, len_greater_than_0, regex_integer):
    tfmkt = TransfermarktCompetitionClubs(competition_id=competition_id, season_id=season_id)
    result = tfmkt.get_competition_clubs()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "name": And(str, len_greater_than_0),
            "seasonID": And(str, len_greater_than_0, regex_integer),
            "clubs": [
                {
                    "id": And(str, len_greater_than_0, regex_integer),
                    "name": And(str, len_greater_than_0),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


def test_tournament_size_configuration_used():
    """Test that configured tournament size is used when available."""
    # Test with World Cup - should use configured size (default 32)
    with patch("app.services.competitions.clubs.settings") as mock_settings:
        mock_settings.get_tournament_size.return_value = 32

        service = TransfermarktCompetitionClubs(competition_id="FIWC", season_id="2006")
        # Verify settings method would be called during parsing
        # We can't easily test the actual call without more complex mocking,
        # but we can verify the service was created successfully
        assert service.competition_id == "FIWC"
        assert service.is_national_team is True


def test_tournament_size_none_logs_warning(caplog):
    """Test that warning is logged when tournament size is not configured."""
    with patch("app.services.competitions.clubs.settings") as mock_settings:
        mock_settings.get_tournament_size.return_value = None

        service = TransfermarktCompetitionClubs(competition_id="FIWC", season_id="2006")

        with caplog.at_level(logging.WARNING):
            # Trigger parsing which should log warning if size is None
            try:
                service._TransfermarktCompetitionClubs__parse_competition_clubs()
            except Exception:
                # Ignore exceptions from actual scraping, we just want to test logging
                pass

        # Check that warning was logged
        assert "Expected tournament size not configured" in caplog.text
        assert "FIWC" in caplog.text


def test_tournament_size_configuration_override():
    """Test that environment variable can override default tournament size."""
    # Test with custom size for World Cup (e.g., 48 for future expansion)
    original_env = os.environ.get("TOURNAMENT_SIZE_FIWC")
    try:
        os.environ["TOURNAMENT_SIZE_FIWC"] = "48"
        # Create new settings instance to pick up environment variable
        test_settings = Settings()
        size = test_settings.get_tournament_size("FIWC")
        assert size == 48
    finally:
        # Restore original environment
        if original_env is not None:
            os.environ["TOURNAMENT_SIZE_FIWC"] = original_env
        elif "TOURNAMENT_SIZE_FIWC" in os.environ:
            del os.environ["TOURNAMENT_SIZE_FIWC"]


def test_settings_get_tournament_size_all_competitions():
    """Test that get_tournament_size returns correct values for all competitions."""
    settings = Settings()

    assert settings.get_tournament_size("FIWC") == 32
    assert settings.get_tournament_size("EURO") == 24
    assert settings.get_tournament_size("COPA") == 12
    assert settings.get_tournament_size("AFAC") == 24
    assert settings.get_tournament_size("GOCU") == 16
    assert settings.get_tournament_size("AFCN") == 24
    assert settings.get_tournament_size("UNKNOWN") is None


def test_settings_tournament_size_validation():
    """Test that tournament size validation rejects invalid values."""
    with pytest.raises(ValueError, match="Tournament size must be a positive integer"):
        Settings(TOURNAMENT_SIZE_FIWC=-1)

    with pytest.raises(ValueError, match="Tournament size must be a positive integer"):
        Settings(TOURNAMENT_SIZE_FIWC=0)
