from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Schema

from app.services.competitions.clubs import TransfermarktCompetitionClubs


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
