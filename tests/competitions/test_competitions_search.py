import pytest
from fastapi import HTTPException

from app.services.competitions.search import TransfermarktCompetitionSearch


def test_competitions_search_0():
    with pytest.raises(HTTPException):
        TransfermarktCompetitionSearch(query="0")


def test_competitions_search_serie_a():
    tfmkt = TransfermarktCompetitionSearch(query="Serie A")
    result = tfmkt.search_competitions()

    expected = {
        "query": "Serie A",
        "pageNumber": 1,
        "lastPageNumber": 2,
        "results": [
            {
                "id": "IT1",
                "name": "Serie A",
                "country": "Italy",
                "continent": "UEFA",
                "clubs": "20",
                "players": "598",
                "marketValue": "€4.50bn",
            },
            {
                "id": "BRA1",
                "name": "Campeonato Brasileiro Série A",
                "country": "Brazil",
                "continent": "CONMEBOL",
                "clubs": "20",
                "players": "670",
                "marketValue": "€1.46bn",
            },
            {
                "id": "BCP1",
                "name": "Campeonato Paulista - Série A1",
                "country": "Brazil",
                "continent": "CONMEBOL",
                "clubs": "16",
                "players": "474",
                "marketValue": "€538.95m",
            },
            {
                "id": "BCPF",
                "name": "Campeonato Paulista - Série A1 - Fase final",
                "country": "Brazil",
                "continent": "CONMEBOL",
                "clubs": "8",
                "players": "240",
                "marketValue": "€447.75m",
            },
            {
                "id": "EL1A",
                "name": "LigaPro Serie A Primera Etapa",
                "country": "Ecuador",
                "continent": "CONMEBOL",
                "clubs": "16",
                "players": "470",
                "marketValue": "€173.38m",
            },
            {
                "id": "EL1S",
                "name": "LigaPro Serie A Segunda Etapa",
                "country": "Ecuador",
                "continent": "CONMEBOL",
                "clubs": "16",
                "players": "470",
                "marketValue": "€173.38m",
            },
            {
                "id": "BCP2",
                "name": "Campeonato Paulista - Troféu Independência",
                "country": "Brazil",
                "continent": "CONMEBOL",
                "clubs": "6",
                "players": "181",
                "marketValue": "€24.10m",
            },
            {
                "id": "PT3A",
                "name": "Liga 3",
                "country": "Portugal",
                "continent": "UEFA",
                "clubs": "20",
                "players": "571",
                "marketValue": "€19.13m",
            },
            {
                "id": "POSB",
                "name": "Serie B Play-off",
                "country": "Italy",
                "continent": "",
                "clubs": "",
                "players": "",
                "marketValue": "",
            },
            {
                "id": "ECPE",
                "name": "Serie A Primera Etapa",
                "country": "Ecuador",
                "continent": "",
                "clubs": "",
                "players": "",
                "marketValue": "",
            },
        ],
    }

    assert result == expected
