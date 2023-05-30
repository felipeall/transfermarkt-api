from datetime import datetime

import pytest
from fastapi import HTTPException

from app.services.players.profile import TransfermarktPlayerProfile


def test_players_profile_id_0():
    tfmkt = TransfermarktPlayerProfile(player_id="0")

    with pytest.raises(HTTPException):
        tfmkt.get_player_profile()


def test_players_profile_id_3373():
    tfmkt = TransfermarktPlayerProfile(player_id="3373")
    result = tfmkt.get_player_profile()
    last_update = result.pop("lastUpdate")

    expected = {
        "url": "/ronaldinho/profil/spieler/3373",
        "id": "3373",
        "name": "Ronaldinho",
        "fullName": "Ronaldo de Assís Moreira",
        "imageURL": "https://img.a.transfermarkt.technology/portrait/header/3373-1515762355.jpg?lm=1",
        "dateOfBirth": "Mar 21, 1980",
        "placeOfBirth": {"city": "Porto Alegre", "country": "Brazil"},
        "age": "43",
        "height": "1,79m",
        "citizenship": ["Brazil", "Spain"],
        "isRetired": True,
        "retiredSince": "Jan 16, 2018",
        "position": {"main": "Left Winger", "other": ["Attacking Midfield", "Second Striker"]},
        "foot": "right",
        "club": {
            "name": "Retired",
            "lastClub": "Fluminense Football Club",
            "lastClubId": "2462",
            "mostGamesFor": "Barcelona",
        },
        "marketValue": {"current": "-", "highest": "€80.00m"},
        "outfitter": "Nike",
        "socialMedia": [
            "http://twitter.com/10Ronaldinho",
            "http://facebook.com/ronaldinho/",
            "http://instagram.com/ronaldinho/",
            "http://www.ronaldinho.com/",
            "http://www.tiktok.com/@ronaldinho",
        ],
    }

    assert isinstance(last_update, datetime)
    assert result == expected


def test_players_profile_id_28003():
    tfmkt = TransfermarktPlayerProfile(player_id="28003")
    result = tfmkt.get_player_profile()
    last_update = result.pop("lastUpdate")

    expected = {
        "url": "/lionel-messi/profil/spieler/28003",
        "id": "28003",
        "name": "Messi",
        "nameInHomeCountry": "Lionel Andrés Messi Cuccitini",
        "imageURL": "https://img.a.transfermarkt.technology/portrait/header/28003-1671435885.jpg?lm=1",
        "dateOfBirth": "Jun 24, 1987",
        "placeOfBirth": {"city": "Rosario", "country": "Argentina"},
        "age": "35",
        "height": "1,70m",
        "citizenship": ["Argentina", "Spain"],
        "isRetired": False,
        "position": {"main": "Right Winger", "other": ["Centre-Forward", "Second Striker"]},
        "foot": "left",
        "shirtNumber": "#30",
        "club": {
            "id": "583",
            "name": "Paris SG",
            "joined": "Aug 10, 2021",
            "contractExpires": "Jun 30, 2023",
            "contractOption": "Option for a further year",
        },
        "marketValue": {"current": "€45.00m", "highest": "€180.00m"},
        "outfitter": "adidas",
        "socialMedia": ["http://www.facebook.com/LeoMessi", "http://instagram.com/leomessi", "http://www.leomessi.com"],
    }

    assert isinstance(last_update, datetime)
    assert result == expected
