from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Optional, Schema

from app.services.players.stats import TransfermarktPlayerStats


def test_players_profile_not_found():
    with pytest.raises(HTTPException):
        TransfermarktPlayerStats(player_id="0")


@pytest.mark.parametrize("player_id", ["3373", "8198", "68290"])
def test_get_player_stats(player_id, len_greater_than_0, regex_integer):
    tfmkt = TransfermarktPlayerStats(player_id=player_id)
    result = tfmkt.get_player_stats()

    expected_schema = Schema(
        {
            "id": str,
            "stats": [
                {
                    "competitionID": And(str, len_greater_than_0),
                    "clubID": And(str, len_greater_than_0, regex_integer),
                    "seasonID": And(str, len_greater_than_0),
                    "competitionName": And(str, len_greater_than_0),
                    Optional("appearances"): And(str, len_greater_than_0, regex_integer),
                    Optional("goals"): And(str, len_greater_than_0, regex_integer),
                    Optional("assists"): And(str, len_greater_than_0, regex_integer),
                    Optional("yellowCards"): And(str, len_greater_than_0, regex_integer),
                    Optional("secondYellowCards"): And(str, len_greater_than_0, regex_integer),
                    Optional("redCards"): And(str, len_greater_than_0, regex_integer),
                    Optional("minutesPlayed"): And(str, len_greater_than_0),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
    assert any("appearances" in stat for stat in result.get("stats"))
    assert any("goals" in stat for stat in result.get("stats"))
    assert any("assists" in stat for stat in result.get("stats"))
    assert any("yellowCards" in stat for stat in result.get("stats"))
    assert any("secondYellowCards" in stat for stat in result.get("stats"))
    assert any("redCards" in stat for stat in result.get("stats"))
    assert any("minutesPlayed" in stat for stat in result.get("stats"))


@pytest.mark.parametrize("player_id", ["5023", "13811"])
def test_get_player_stats_goalkeeper(player_id, len_greater_than_0, regex_integer):
    tfmkt = TransfermarktPlayerStats(player_id=player_id)
    result = tfmkt.get_player_stats()

    expected_schema = Schema(
        {
            "id": str,
            "stats": [
                {
                    "competitionID": And(str, len_greater_than_0),
                    "clubID": And(str, len_greater_than_0, regex_integer),
                    "seasonID": And(str, len_greater_than_0),
                    "competitionName": And(str, len_greater_than_0),
                    Optional("appearances"): And(str, len_greater_than_0, regex_integer),
                    Optional("goals"): And(str, len_greater_than_0, regex_integer),
                    Optional("yellowCards"): And(str, len_greater_than_0, regex_integer),
                    Optional("secondYellowCards"): And(str, len_greater_than_0, regex_integer),
                    Optional("redCards"): And(str, len_greater_than_0, regex_integer),
                    Optional("goalsConceded"): And(str, len_greater_than_0, regex_integer),
                    Optional("cleanSheets"): And(str, len_greater_than_0, regex_integer),
                    Optional("minutesPlayed"): And(str, len_greater_than_0),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
    assert any("appearances" in stat for stat in result.get("stats"))
    assert any("yellowCards" in stat for stat in result.get("stats"))
    assert any("redCards" in stat for stat in result.get("stats"))
    assert any("goalsConceded" in stat for stat in result.get("stats"))
    assert any("cleanSheets" in stat for stat in result.get("stats"))
    assert any("minutesPlayed" in stat for stat in result.get("stats"))
