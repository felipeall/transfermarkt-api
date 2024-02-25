from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Optional, Schema

from app.services.players.achievements import TransfermarktPlayerAchievements


def test_get_player_achievements_not_found():
    with pytest.raises(HTTPException):
        TransfermarktPlayerAchievements(player_id="0")


@pytest.mark.parametrize("player_id", ["28003", "8198"])
def test_get_player_achievements(player_id, len_greater_than_0, regex_integer, regex_date_mmm_dd_yyyy):
    tfmkt = TransfermarktPlayerAchievements(player_id="28003")
    result = tfmkt.get_player_achievements()

    expected_schema = Schema(
        {
            "id": And(str, regex_integer),
            "achievements": [
                {
                    "title": And(str, len_greater_than_0),
                    "count": int,
                    "details": [
                        {
                            "season": {
                                Optional("id"): And(str, regex_integer),
                                "name": And(str, len_greater_than_0),
                            },
                            Optional("club"): {
                                Optional("id"): And(str, regex_integer),
                                Optional("name"): And(str, len_greater_than_0),
                            },
                            Optional("competition"): {
                                Optional("id"): And(str, len_greater_than_0),
                                Optional("name"): And(str, len_greater_than_0),
                            },
                        },
                    ],
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
