from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from schema import And, Or, Schema

from app.services.clubs.players import TransfermarktClubPlayers


def test_get_club_players_not_found():
    with pytest.raises(HTTPException):
        TransfermarktClubPlayers(club_id="0")


@pytest.mark.parametrize("club_id,season_id", [("418", None), ("131", "2014"), ("210", "2017")])
@patch("app.utils.utils.clean_response", side_effect=lambda x: x)
def test_get_club_players(
    mock_clean_response,
    club_id,
    season_id,
    regex_date_mmm_dd_yyyy,
    regex_integer,
    regex_height,
    regex_market_value,
    len_greater_than_0,
):
    tfmkt = TransfermarktClubPlayers(club_id=club_id, season_id=season_id)
    result = tfmkt.get_club_players()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "players": [
                {
                    "id": And(str, len_greater_than_0),
                    "name": And(str, len_greater_than_0),
                    "position": And(str, len_greater_than_0),
                    "dateOfBirth": And(str, len_greater_than_0, regex_date_mmm_dd_yyyy),
                    "age": And(str, len_greater_than_0, regex_integer),
                    "nationality": And(list, len_greater_than_0),
                    "currentClub": Or(None, And(str, len_greater_than_0)),
                    "height": And(str, len_greater_than_0, regex_height),
                    "foot": And(str, len_greater_than_0),
                    "joinedOn": Or("", And(str, len_greater_than_0, regex_date_mmm_dd_yyyy)),
                    "joined": Or("", And(str, len_greater_than_0)),
                    "signedFrom": Or("", And(str, len_greater_than_0)),
                    "contract": Or(None, And(str, regex_date_mmm_dd_yyyy)),
                    "marketValue": And(str, len_greater_than_0, regex_market_value),
                    "status": Or("", And(str, len_greater_than_0)),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
