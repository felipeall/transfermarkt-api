import pytest
from fastapi import HTTPException

from app.services.competitions.search import TransfermarktCompetitionSearch


def test_players_search_0():
    tfmkt = TransfermarktCompetitionSearch(query="0")

    with pytest.raises(HTTPException):
        tfmkt.search_competitions()


def test_players_search_ronaldo():
    tfmkt = TransfermarktCompetitionSearch(query="serie a")
    result = tfmkt.search_competitions()

    expected = [
        {
            "id": "IT1",
            "name": "Serie A",
            "country": "Italy",
            "continent": "UEFA",
            "clubs": "20",
            "players": "561",
            "marketValue": "€4.63bn",
        },
        {
            "id": "BRA1",
            "name": "Campeonato Brasileiro Série A",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "20",
            "players": "661",
            "marketValue": "€1.41bn",
        },
        {
            "id": "BCP1",
            "name": "Campeonato Paulista - Série A1",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "16",
            "players": "439",
            "marketValue": "€531.43m",
        },
        {
            "id": "BCPF",
            "name": "Campeonato Paulista - Série A1 - Fase final",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "8",
            "players": "236",
            "marketValue": "€429.18m",
        },
        {
            "id": "POSB",
            "name": "Serie B Play-off",
            "country": "Italy",
            "continent": "UEFA",
            "clubs": "6",
            "players": "169",
            "marketValue": "€184.75m",
        },
        {
            "id": "EL1A",
            "name": "LigaPro Serie A Primera Etapa",
            "country": "Ecuador",
            "continent": "CONMEBOL",
            "clubs": "16",
            "players": "459",
            "marketValue": "€165.30m",
        },
        {
            "id": "PT3A",
            "name": "3. Liga",
            "country": "Portugal",
            "continent": "UEFA",
            "clubs": "24",
            "players": "685",
            "marketValue": "€29.23m",
        },
        {
            "id": "BCP2",
            "name": "Campeonato Paulista - Troféu Independência",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "6",
            "players": "167",
            "marketValue": "€22.90m",
        },
        {"id": "ECPE", "name": "Serie A Primera Etapa", "country": "Ecuador"},
        {"id": "ECSE", "name": "Serie A Segunda Etapa", "country": "Ecuador"},
    ]

    print(result)
    assert result == expected
