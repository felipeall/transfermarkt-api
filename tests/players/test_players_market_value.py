import pytest
from fastapi import HTTPException

from app.services.players.market_value import TransfermarktPlayerMarketValue


def test_players_market_value_id_3373():
    tfmkt = TransfermarktPlayerMarketValue(player_id="3373")
    result = tfmkt.get_player_market_value()

    expected = {
        "id": "3373",
        "playerName": "Ronaldinho",
        "marketValueHistory": [
            {"age": "24", "date": "Oct 4, 2004", "value": "€38.00m"},
            {"age": "24", "date": "Dec 20, 2004", "value": "€50.00m"},
            {"age": "25", "date": "Jan 20, 2006", "value": "€70.00m"},
            {"age": "27", "date": "Sep 9, 2007", "value": "€80.00m"},
            {"age": "27", "date": "Feb 4, 2008", "value": "€50.00m"},
            {"age": "28", "date": "Jul 10, 2008", "value": "€35.00m"},
            {"age": "28", "date": "Feb 6, 2009", "value": "€33.00m"},
            {"age": "29", "date": "Aug 6, 2009", "value": "€28.50m"},
            {"age": "29", "date": "Oct 29, 2009", "value": "€25.00m"},
            {"age": "29", "date": "Jan 27, 2010", "value": "€27.50m"},
            {"age": "30", "date": "Jan 12, 2011", "value": "€12.00m"},
            {"age": "31", "date": "May 30, 2011", "value": "€8.00m"},
            {"age": "31", "date": "Dec 8, 2011", "value": "€7.00m"},
            {"age": "32", "date": "May 24, 2012", "value": "€4.00m"},
            {"age": "32", "date": "Jul 29, 2012", "value": "€3.00m"},
            {"age": "32", "date": "Dec 5, 2012", "value": "€2.00m"},
            {"age": "33", "date": "Aug 26, 2013", "value": "€1.50m"},
            {"age": "34", "date": "Mar 28, 2014", "value": "€1.50m"},
            {"age": "34", "date": "Sep 1, 2014", "value": "€1.50m"},
            {"age": "36", "date": "Feb 3, 2017", "value": "-"},
        ],
    }

    assert result == expected


def test_players_market_value_fail():
    tfmkt = TransfermarktPlayerMarketValue(player_id="0")

    with pytest.raises(HTTPException):
        tfmkt.get_player_market_value()
