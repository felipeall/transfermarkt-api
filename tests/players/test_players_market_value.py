import pytest
from fastapi import HTTPException

from app.services.players.market_value import TransfermarktPlayerMarketValue


def test_players_market_value_id_0():
    tfmkt = TransfermarktPlayerMarketValue(player_id="0")

    with pytest.raises(HTTPException):
        tfmkt.get_player_market_value()


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


def test_players_market_value_id_28003():
    tfmkt = TransfermarktPlayerMarketValue(player_id="28003")
    result = tfmkt.get_player_market_value()

    expected = {
        "id": "28003",
        "playerName": "Messi",
        "marketValue": "€35.00m",
        "marketValueHistory": [
            {"age": "17", "date": "Dec 20, 2004", "value": "€3.00m"},
            {"age": "18", "date": "Dec 28, 2005", "value": "€5.00m"},
            {"age": "18", "date": "Jan 20, 2006", "value": "€15.00m"},
            {"age": "20", "date": "Jul 26, 2007", "value": "€40.00m"},
            {"age": "20", "date": "Sep 12, 2007", "value": "€60.00m"},
            {"age": "20", "date": "Feb 4, 2008", "value": "€55.00m"},
            {"age": "21", "date": "Jul 10, 2008", "value": "€55.00m"},
            {"age": "21", "date": "Jan 26, 2009", "value": "€55.00m"},
            {"age": "21", "date": "Apr 28, 2009", "value": "€60.00m"},
            {"age": "22", "date": "Jul 22, 2009", "value": "€70.00m"},
            {"age": "22", "date": "Dec 3, 2009", "value": "€70.00m"},
            {"age": "22", "date": "Jan 7, 2010", "value": "€80.00m"},
            {"age": "22", "date": "Apr 12, 2010", "value": "€80.00m"},
            {"age": "23", "date": "Aug 27, 2010", "value": "€100.00m"},
            {"age": "23", "date": "Feb 4, 2011", "value": "€100.00m"},
            {"age": "24", "date": "Jul 29, 2011", "value": "€100.00m"},
            {"age": "24", "date": "Feb 3, 2012", "value": "€100.00m"},
            {"age": "25", "date": "Aug 7, 2012", "value": "€120.00m"},
            {"age": "25", "date": "Jan 10, 2013", "value": "€120.00m"},
            {"age": "25", "date": "Jun 12, 2013", "value": "€120.00m"},
            {"age": "26", "date": "Jan 23, 2014", "value": "€120.00m"},
            {"age": "27", "date": "Jul 20, 2014", "value": "€120.00m"},
            {"age": "27", "date": "Jan 23, 2015", "value": "€120.00m"},
            {"age": "28", "date": "Jul 1, 2015", "value": "€120.00m"},
            {"age": "28", "date": "Feb 22, 2016", "value": "€120.00m"},
            {"age": "29", "date": "Jul 15, 2016", "value": "€120.00m"},
            {"age": "29", "date": "Jan 24, 2017", "value": "€120.00m"},
            {"age": "29", "date": "Jun 5, 2017", "value": "€120.00m"},
            {"age": "30", "date": "Jan 1, 2018", "value": "€180.00m"},
            {"age": "30", "date": "May 30, 2018", "value": "€180.00m"},
            {"age": "31", "date": "Dec 21, 2018", "value": "€160.00m"},
            {"age": "31", "date": "Jun 11, 2019", "value": "€150.00m"},
            {"age": "32", "date": "Dec 20, 2019", "value": "€140.00m"},
            {"age": "32", "date": "Apr 8, 2020", "value": "€112.00m"},
            {"age": "33", "date": "Oct 8, 2020", "value": "€100.00m"},
            {"age": "33", "date": "Jan 5, 2021", "value": "€80.00m"},
            {"age": "33", "date": "Jun 10, 2021", "value": "€80.00m"},
            {"age": "34", "date": "Dec 16, 2021", "value": "€60.00m"},
            {"age": "34", "date": "May 30, 2022", "value": "€50.00m"},
            {"age": "35", "date": "Nov 2, 2022", "value": "€50.00m"},
            {"age": "35", "date": "Mar 27, 2023", "value": "€45.00m"},
            {"age": "36", "date": "Jun 27, 2023", "value": "€35.00m"},
        ],
        "ranking": {
            "Worldwide": "171",
            "MLS": "1",
            "Miami": "1",
            "Argentina": "8",
            "Right Winger": "14",
            "Year 1987": "1",
        },
        "lastUpdate": "Jun 27, 2023",
    }

    assert result == expected
