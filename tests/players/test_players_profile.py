from datetime import datetime

import pytest
from fastapi import HTTPException
from schema import And, Schema

from app.services.players.profile import TransfermarktPlayerProfile


def test_players_profile_not_found():
    with pytest.raises(HTTPException):
        TransfermarktPlayerProfile(player_id="0")


def test_get_player_profile_28003(len_greater_than_0):
    tfmk = TransfermarktPlayerProfile(player_id="28003")
    result = tfmk.get_player_profile()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "url": And(str, len_greater_than_0),
            "name": And(str, len_greater_than_0),
            "description": And(str, len_greater_than_0),
            "nameInHomeCountry": And(str, len_greater_than_0),
            "imageURL": And(str, len_greater_than_0),
            "dateOfBirth": And(str, len_greater_than_0),
            "placeOfBirth": {
                "city": And(str, len_greater_than_0),
                "country": And(str, len_greater_than_0),
            },
            "age": And(str, len_greater_than_0),
            "height": And(str, len_greater_than_0),
            "citizenship": And(list, len_greater_than_0),
            "isRetired": bool,
            "position": {
                "main": And(str, len_greater_than_0),
                "other": And(list, len_greater_than_0),
            },
            "foot": And(str, len_greater_than_0),
            "shirtNumber": And(str, len_greater_than_0),
            "club": {
                "id": And(str, len_greater_than_0),
                "name": And(str, len_greater_than_0),
                "joined": And(str, len_greater_than_0),
                "contractExpires": And(str, len_greater_than_0),
            },
            "marketValue": And(str, len_greater_than_0),
            "agent": {
                "name": And(str, len_greater_than_0),
            },
            "outfitter": And(str, len_greater_than_0),
            "socialMedia": And(list, len_greater_than_0),
            "relatives": [
                {
                    "id": And(str, len_greater_than_0),
                    "url": And(str, len_greater_than_0),
                    "name": And(str, len_greater_than_0),
                    "profileType": And(str, len_greater_than_0),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


def test_get_player_profile_8198(len_greater_than_0):
    tfmk = TransfermarktPlayerProfile(player_id="8198")
    result = tfmk.get_player_profile()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "url": And(str, len_greater_than_0),
            "name": And(str, len_greater_than_0),
            "description": And(str, len_greater_than_0),
            "fullName": And(str, len_greater_than_0),
            "imageURL": And(str, len_greater_than_0),
            "dateOfBirth": And(str, len_greater_than_0),
            "placeOfBirth": {
                "city": And(str, len_greater_than_0),
                "country": And(str, len_greater_than_0),
            },
            "age": And(str, len_greater_than_0),
            "height": And(str, len_greater_than_0),
            "citizenship": And(list, len_greater_than_0),
            "isRetired": bool,
            "position": {
                "main": And(str, len_greater_than_0),
                "other": And(list, len_greater_than_0),
            },
            "foot": And(str, len_greater_than_0),
            "shirtNumber": And(str, len_greater_than_0),
            "club": {
                "id": And(str, len_greater_than_0),
                "name": And(str, len_greater_than_0),
                "joined": And(str, len_greater_than_0),
                "contractExpires": And(str, len_greater_than_0),
            },
            "marketValue": And(str, len_greater_than_0),
            "agent": {
                "name": And(str, len_greater_than_0),
                "url": And(str, len_greater_than_0),
            },
            "outfitter": And(str, len_greater_than_0),
            "socialMedia": And(list, len_greater_than_0),
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


def test_get_player_profile_68290(len_greater_than_0):
    tfmk = TransfermarktPlayerProfile(player_id="68290")
    result = tfmk.get_player_profile()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "url": And(str, len_greater_than_0),
            "name": And(str, len_greater_than_0),
            "description": And(str, len_greater_than_0),
            "fullName": And(str, len_greater_than_0),
            "imageURL": And(str, len_greater_than_0),
            "dateOfBirth": And(str, len_greater_than_0),
            "placeOfBirth": {
                "city": And(str, len_greater_than_0),
                "country": And(str, len_greater_than_0),
            },
            "age": And(str, len_greater_than_0),
            "height": And(str, len_greater_than_0),
            "citizenship": And(list, len_greater_than_0),
            "isRetired": bool,
            "position": {
                "main": And(str, len_greater_than_0),
                "other": And(list, len_greater_than_0),
            },
            "foot": And(str, len_greater_than_0),
            "shirtNumber": And(str, len_greater_than_0),
            "club": {
                "id": And(str, len_greater_than_0),
                "name": And(str, len_greater_than_0),
                "joined": And(str, len_greater_than_0),
                "contractExpires": And(str, len_greater_than_0),
                "contractOption": And(str, len_greater_than_0),
            },
            "marketValue": And(str, len_greater_than_0),
            "agent": {
                "name": And(str, len_greater_than_0),
            },
            "outfitter": And(str, len_greater_than_0),
            "socialMedia": And(list, len_greater_than_0),
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


def test_get_player_profile_3373(len_greater_than_0):
    tfmk = TransfermarktPlayerProfile(player_id="3373")
    result = tfmk.get_player_profile()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "url": And(str, len_greater_than_0),
            "name": And(str, len_greater_than_0),
            "description": And(str, len_greater_than_0),
            "fullName": And(str, len_greater_than_0),
            "imageURL": And(str, len_greater_than_0),
            "dateOfBirth": And(str, len_greater_than_0),
            "placeOfBirth": {
                "city": And(str, len_greater_than_0),
                "country": And(str, len_greater_than_0),
            },
            "age": And(str, len_greater_than_0),
            "height": And(str, len_greater_than_0),
            "citizenship": And(list, len_greater_than_0),
            "isRetired": bool,
            "retiredSince": And(str, len_greater_than_0),
            "position": {
                "main": And(str, len_greater_than_0),
                "other": And(list, len_greater_than_0),
            },
            "foot": And(str, len_greater_than_0),
            "club": {
                "name": And(str, len_greater_than_0),
                "joined": And(str, len_greater_than_0),
                "lastClubID": And(str, len_greater_than_0),
                "lastClubName": And(str, len_greater_than_0),
                "mostGamesFor": And(str, len_greater_than_0),
            },
            "outfitter": And(str, len_greater_than_0),
            "socialMedia": And(list, len_greater_than_0),
            "trainerProfile": {
                "id": And(str, len_greater_than_0),
                "url": And(str, len_greater_than_0),
                "position": And(str, len_greater_than_0),
            },
            "relatives": [
                {
                    "id": And(str, len_greater_than_0),
                    "url": And(str, len_greater_than_0),
                    "name": And(str, len_greater_than_0),
                    "profileType": And(str, len_greater_than_0),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
