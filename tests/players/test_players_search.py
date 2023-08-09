import pytest
from fastapi import HTTPException

from app.services.players.search import TransfermarktPlayerSearch


def test_players_search_0():
    tfmkt = TransfermarktPlayerSearch(query="0")

    with pytest.raises(HTTPException):
        tfmkt.search_players()


def test_players_search_ronaldo():
    tfmkt = TransfermarktPlayerSearch(query="Ronaldo")
    result = tfmkt.search_players()

    expected = [
        {
            "id": "8198",
            "url": "/cristiano-ronaldo/profil/spieler/8198",
            "name": "Cristiano Ronaldo",
            "club": {"id": "18544", "name": "Al-Nassr FC"},
            "position": "CF",
            "age": "38",
            "nationality": ["Portugal"],
            "marketValue": "€15.00m",
        },
        {
            "id": "3140",
            "url": "/ronaldo/profil/spieler/3140",
            "name": "Ronaldo",
            "club": {"id": "515", "name": "Retired"},
            "position": "CF",
            "age": "46",
            "nationality": ["Brazil", "Spain"],
            "marketValue": "-",
        },
        {
            "id": "3373",
            "url": "/ronaldinho/profil/spieler/3373",
            "name": "Ronaldinho",
            "club": {"id": "515", "name": "Retired"},
            "position": "LW",
            "age": "43",
            "nationality": ["Brazil", "Spain"],
            "marketValue": "-",
        },
        {
            "id": "102589",
            "url": "/ronaldao/profil/spieler/102589",
            "name": "Ronaldao",
            "club": {"id": "515", "name": "Retired"},
            "position": "CB",
            "age": "58",
            "nationality": ["Brazil"],
            "marketValue": "-",
        },
        {
            "id": "27300",
            "url": "/rolando/profil/spieler/27300",
            "name": "Rolando",
            "club": {"id": "515", "name": "Retired"},
            "position": "CB",
            "age": "37",
            "nationality": ["Portugal", "Cape Verde"],
            "marketValue": "-",
        },
        {
            "id": "356772",
            "url": "/ronaldo-luiz/profil/spieler/356772",
            "name": "Ronaldo Luiz",
            "club": {"id": "515", "name": "Retired"},
            "position": "LB",
            "age": "56",
            "nationality": ["Brazil"],
            "marketValue": "-",
        },
        {
            "id": "32213",
            "url": "/naldo/profil/spieler/32213",
            "name": "Naldo",
            "club": {"id": "515", "name": "Retired"},
            "position": "CB",
            "age": "40",
            "nationality": ["Brazil", "Germany"],
            "marketValue": "-",
        },
        {
            "id": "434676",
            "url": "/ronaldo-vieira/profil/spieler/434676",
            "name": "Ronaldo Vieira",
            "club": {"id": "1038", "name": "UC Sampdoria"},
            "position": "CM",
            "age": "25",
            "nationality": ["England", "Guinea-Bissau"],
            "marketValue": "€2.00m",
        },
        {
            "id": "405768",
            "url": "/ronaldo/profil/spieler/405768",
            "name": "Ronaldo",
            "club": {"id": "1062", "name": "Shimizu S-Pulse"},
            "position": "DM",
            "age": "26",
            "nationality": ["Brazil"],
            "marketValue": "€500k",
        },
        {
            "id": "6887",
            "url": "/ronaldo/profil/spieler/6887",
            "name": "Ronaldo",
            "club": {"id": "515", "name": "Retired"},
            "position": "CB",
            "age": "49",
            "nationality": ["Brazil", "Portugal"],
            "marketValue": "-",
        },
    ]

    assert result == expected
