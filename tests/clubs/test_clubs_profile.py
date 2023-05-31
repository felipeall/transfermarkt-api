import pytest
from fastapi import HTTPException

from app.services.clubs.profile import TransfermarktClubProfile


def test_clubs_profile_id_0():
    tfmkt = TransfermarktClubProfile(club_id="0")

    with pytest.raises(HTTPException):
        tfmkt.get_club_profile()


def test_clubs_profile_id_210():
    tfmkt = TransfermarktClubProfile(club_id="210")
    result = tfmkt.get_club_profile()

    expected = {
        "id": "210",
        "url": "/gremio-porto-alegre/startseite/verein/210",
        "name": "Grêmio Foot-Ball Porto Alegrense",
        "officialName": "Grêmio Foot-Ball Porto Alegrense",
        "image": "https://tmssl.akamaized.net/images/wappen/big/210.png",
        "addressLine1": "Rua Largo dos Campeões 1",
        "addressLine2": "90880-440 Porto Alegre",
        "addressLine3": "Brazil",
        "tel": "+55 51 32172244",
        "fax": "+55 51 32232364",
        "website": "www.gremio.net",
        "foundedOn": "Sep 15, 1903",
        "members": "148.613",
        "membersDate": "Jan 26, 2019",
        "stadiumName": "Arena do Grêmio",
        "stadiumSeats": "60.540",
        "currentTransferRecord": "+€155k",
        "currentMarketValue": "€54.10m",
        "squad": {"size": "36", "averageAge": "26.3", "foreigners": "5", "nationalTeamPlayers": "3"},
        "league": {
            "id": "BRA1",
            "name": "Campeonato Brasileiro Série A",
            "countryID": "2",
            "countryName": "Brazil",
            "tier": "First Tier",
        },
    }

    assert result == expected
