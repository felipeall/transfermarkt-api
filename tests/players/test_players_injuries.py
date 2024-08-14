from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Optional, Schema

from app.services.players.injuries import TransfermarktPlayerInjuries


def test_get_player_injuries_not_found():
    with pytest.raises(HTTPException):
        TransfermarktPlayerInjuries(player_id="0")


@pytest.mark.parametrize(
    "player_id,page_number",
    [("28003", 1), ("28003", 2), ("28003", 3), ("28003", 999), ("8198", 1), ("8198", 999)],
)
def test_get_player_injuries(player_id, page_number, len_greater_than_0, regex_integer, regex_date_mmm_dd_yyyy):
    tfmkt = TransfermarktPlayerInjuries(player_id=player_id, page_number=page_number)
    result = tfmkt.get_player_injuries()

    expected_schema = Schema(
        {
            "id": And(str, regex_integer),
            "pageNumber": int,
            "lastPageNumber": int,
            "injuries": [
                {
                    "season": And(str, len_greater_than_0),
                    "injury": And(str, len_greater_than_0),
                    "from": And(str, len_greater_than_0, regex_date_mmm_dd_yyyy),
                    Optional("until"): And(str, len_greater_than_0, regex_date_mmm_dd_yyyy),
                    "days": And(str, len_greater_than_0),
                    Optional("gamesMissed"): And(str, len_greater_than_0, regex_integer),
                    Optional("gamesMissedClubs"): list[str],
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
