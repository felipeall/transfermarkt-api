from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.players.transfers import TransfermarktPlayerTransfers


def test_get_player_transfers_id_0():
    tfmkt = TransfermarktPlayerTransfers(player_id="0")

    with pytest.raises(HTTPException):
        tfmkt.get_player_transfers()


def test_get_player_transfers_id_3373():
    tfmkt = TransfermarktPlayerTransfers(player_id="3373")
    result = tfmkt.get_player_transfers()
    last_update = result.pop("lastUpdate")

    expected = {
        "id": "3373",
        "name": "Ronaldinho",
        "history": [
            {
                "transferID": "1695687",
                "transferSeason": "17/18",
                "transferDate": "Jan 16, 2018",
                "oldClubID": "515",
                "oldClubName": "Without Club",
                "newClubID": "123",
                "newClubName": "Retired",
                "marketValue": "-",
                "fee": "-",
            },
            {
                "transferID": "1352957",
                "transferSeason": "15/16",
                "transferDate": "Sep 29, 2015",
                "oldClubID": "2462",
                "oldClubName": "Fluminense",
                "newClubID": "515",
                "newClubName": "Without Club",
                "marketValue": "€1.50m",
                "fee": "-",
            },
            {
                "transferID": "1264183",
                "transferSeason": "15/16",
                "transferDate": "Jul 11, 2015",
                "oldClubID": "4961",
                "oldClubName": "Querétaro FC",
                "newClubID": "2462",
                "newClubName": "Fluminense",
                "marketValue": "€1.50m",
                "fee": "free transfer",
            },
            {
                "transferID": "1097798",
                "transferSeason": "14/15",
                "transferDate": "Sep 5, 2014",
                "oldClubID": "330",
                "oldClubName": "Atlético-MG",
                "newClubID": "4961",
                "newClubName": "Querétaro FC",
                "marketValue": "€1.50m",
                "fee": "free transfer",
            },
            {
                "transferID": "723963",
                "transferSeason": "11/12",
                "transferDate": "Jun 4, 2012",
                "oldClubID": "614",
                "oldClubName": "Flamengo",
                "newClubID": "330",
                "newClubName": "Atlético-MG",
                "marketValue": "€4.00m",
                "fee": "free transfer",
            },
            {
                "transferID": "521934",
                "transferSeason": "10/11",
                "transferDate": "Jan 11, 2011",
                "oldClubID": "5",
                "oldClubName": "AC Milan",
                "newClubID": "614",
                "newClubName": "Flamengo",
                "marketValue": "€27.50m",
                "fee": "€3.00m",
            },
            {
                "transferID": "211889",
                "transferSeason": "08/09",
                "transferDate": "Jul 15, 2008",
                "oldClubID": "131",
                "oldClubName": "Barcelona",
                "newClubID": "5",
                "newClubName": "AC Milan",
                "marketValue": "€35.00m",
                "fee": "€24.15m",
            },
            {
                "transferID": "10553",
                "transferSeason": "03/04",
                "transferDate": "Jul 19, 2003",
                "oldClubID": "583",
                "oldClubName": "Paris SG",
                "newClubID": "131",
                "newClubName": "Barcelona",
                "marketValue": "-",
                "fee": "€32.25m",
            },
            {
                "transferID": "29908",
                "transferSeason": "01/02",
                "transferDate": "Jul 1, 2001",
                "oldClubID": "210",
                "oldClubName": "Grêmio",
                "newClubID": "583",
                "newClubName": "Paris SG",
                "marketValue": "-",
                "fee": "€5.00m",
            },
            {
                "transferID": "29909",
                "transferSeason": "97/98",
                "transferDate": "Jan 1, 1998",
                "oldClubID": "14704",
                "oldClubName": "Grêmio B",
                "newClubID": "210",
                "newClubName": "Grêmio",
                "marketValue": "-",
                "fee": "-",
            },
        ],
    }

    assert isinstance(last_update, datetime)
    assert result == expected


def test_get_player_transfers_id_28003():
    tfmkt = TransfermarktPlayerTransfers(player_id="28003")
    result = tfmkt.get_player_transfers()
    last_update = result.pop("lastUpdate")

    expected = {
        "id": "28003",
        "name": "Messi",
        "history": [
            {
                "transferID": "4418847",
                "transferSeason": "23/24",
                "transferDate": "Jul 1, 2023",
                "oldClubID": "583",
                "oldClubName": "Paris SG",
                "newClubID": "515",
                "newClubName": "Without Club",
                "marketValue": "€45.00m",
                "fee": "-",
            },
            {
                "transferID": "3489998",
                "transferSeason": "21/22",
                "transferDate": "Aug 10, 2021",
                "oldClubID": "131",
                "oldClubName": "Barcelona",
                "newClubID": "583",
                "newClubName": "Paris SG",
                "marketValue": "€80.00m",
                "fee": "free transfer",
            },
            {
                "transferID": "48265",
                "transferSeason": "05/06",
                "transferDate": "Jul 1, 2005",
                "oldClubID": "2464",
                "oldClubName": "Barcelona B",
                "newClubID": "131",
                "newClubName": "Barcelona",
                "marketValue": "€3.00m",
                "fee": "-",
            },
            {
                "transferID": "153557",
                "transferSeason": "03/04",
                "transferDate": "Mar 5, 2004",
                "oldClubID": "63954",
                "oldClubName": "Barcelona C",
                "newClubID": "2464",
                "newClubName": "Barcelona B",
                "marketValue": "-",
                "fee": "-",
            },
            {
                "transferID": "1993882",
                "transferSeason": "03/04",
                "transferDate": "Nov 28, 2003",
                "oldClubID": "2470",
                "oldClubName": "Barça U19",
                "newClubID": "63954",
                "newClubName": "Barcelona C",
                "marketValue": "-",
                "fee": "-",
            },
            {
                "transferID": "1136539",
                "transferSeason": "03/04",
                "transferDate": "Sep 13, 2003",
                "oldClubID": "14321",
                "oldClubName": "Barça U16",
                "newClubID": "2470",
                "newClubName": "Barça U19",
                "marketValue": "-",
                "fee": "-",
            },
            {
                "transferID": "2326361",
                "transferSeason": "02/03",
                "transferDate": "Jul 1, 2002",
                "oldClubID": "70295",
                "oldClubName": "Barça Youth",
                "newClubID": "14321",
                "newClubName": "Barça U16",
                "marketValue": "-",
                "fee": "-",
            },
            {
                "transferID": "181327",
                "transferSeason": "00/01",
                "transferDate": "Jul 1, 2000",
                "oldClubID": "92364",
                "oldClubName": "Newell's Youth",
                "newClubID": "70295",
                "newClubName": "Barça Youth",
                "marketValue": "-",
                "fee": "free transfer",
            },
        ],
        "youthClubs": ["Grandoli FC (1992-1995)", "Newell's Old Boys (1995-2000)"],
    }

    assert isinstance(last_update, datetime)
    assert result == expected
