from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Optional, Schema

from app.services.players.market_value import TransfermarktPlayerMarketValue


def test_get_player_market_value_not_found():
    with pytest.raises(HTTPException):
        TransfermarktPlayerMarketValue(player_id="0")


@pytest.mark.parametrize("player_id", ["8198", "28003"])
def test_get_player_market_value_not_retired(player_id, len_greater_than_0):
    tfmkt = TransfermarktPlayerMarketValue(player_id=player_id)
    result = tfmkt.get_player_market_value()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "marketValue": And(str, len_greater_than_0),
            "marketValueHistory": [
                {
                    "age": And(str, len_greater_than_0),
                    "date": And(str, len_greater_than_0),
                    "clubName": And(str, len_greater_than_0),
                    "value": And(str, len_greater_than_0),
                    "clubID": And(str, len_greater_than_0),
                },
            ],
            "ranking": And(dict, lambda x: len(x) == 6),
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


@pytest.mark.parametrize("player_id", ["3373"])
def test_get_player_market_value_retired(player_id, len_greater_than_0):
    tfmkt = TransfermarktPlayerMarketValue(player_id=player_id)
    result = tfmkt.get_player_market_value()

    expected_schema = Schema(
        {
            "id": str,
            "marketValueHistory": [
                {
                    "age": And(str, len_greater_than_0),
                    "date": And(str, len_greater_than_0),
                    "clubName": And(str, len_greater_than_0),
                    Optional("value"): And(str, len_greater_than_0),
                    "clubID": And(str, len_greater_than_0),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
