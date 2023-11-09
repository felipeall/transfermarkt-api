from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Optional, Schema

from app.services.players.transfers import TransfermarktPlayerTransfers


def test_get_player_transfers_not_found():
    with pytest.raises(HTTPException):
        TransfermarktPlayerTransfers(player_id="0")


@pytest.mark.parametrize("player_id", ["28003", "8198"])
def test_get_player_transfers(player_id, len_greater_than_0, regex_integer, regex_date_mmm_dd_yyyy, regex_market_value):
    tfmkt = TransfermarktPlayerTransfers(player_id=player_id)
    result = tfmkt.get_player_transfers()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0, regex_integer),
            "transfers": [
                {
                    "id": And(str, len_greater_than_0, regex_integer),
                    "season": And(str, len_greater_than_0),
                    "date": And(str, len_greater_than_0, regex_date_mmm_dd_yyyy),
                    "from": {
                        "clubID": And(str, len_greater_than_0, regex_integer),
                        "clubName": And(str, len_greater_than_0),
                    },
                    "to": {
                        "clubID": And(str, len_greater_than_0, regex_integer),
                        "clubName": And(str, len_greater_than_0),
                    },
                    "upcoming": bool,
                    Optional("marketValue"): And(str, len_greater_than_0, regex_market_value),
                    Optional("fee"): And(str, len_greater_than_0),
                },
            ],
            "youthClubs": list,
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
    assert any("marketValue" in stat for stat in result.get("transfers"))
    assert any("fee" in stat for stat in result.get("transfers"))
