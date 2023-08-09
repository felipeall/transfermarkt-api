import pytest
from fastapi import HTTPException

from app.services.competitions.search import TransfermarktCompetitionSearch


def test_players_search_0():
    tfmkt = TransfermarktCompetitionSearch(query="0")

    with pytest.raises(HTTPException):
        tfmkt.search_competitions()


def test_players_search_serie_a():
    tfmkt = TransfermarktCompetitionSearch(query="Serie A")
    result = tfmkt.search_competitions()

    expected = [
        {
            "id": "IT1",
            "name": "Serie A",
            "country": "Italy",
            "continent": "UEFA",
            "clubs": "20",
            "players": "607",
            "marketValue": "€4.59bn",
        },
        {
            "id": "BRA1",
            "name": "Campeonato Brasileiro Série A",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "20",
            "players": "670",
            "marketValue": "€1.47bn",
        },
        {
            "id": "BCP1",
            "name": "Campeonato Paulista - Série A1",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "16",
            "players": "476",
            "marketValue": "€548.45m",
        },
        {
            "id": "BCPF",
            "name": "Campeonato Paulista - Série A1 - Fase final",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "8",
            "players": "238",
            "marketValue": "€457.35m",
        },
        {
            "id": "EL1A",
            "name": "LigaPro Serie A Primera Etapa",
            "country": "Ecuador",
            "continent": "CONMEBOL",
            "clubs": "16",
            "players": "475",
            "marketValue": "€175.30m",
        },
        {
            "id": "EL1S",
            "name": "LigaPro Serie A Segunda Etapa",
            "country": "Ecuador",
            "continent": "CONMEBOL",
            "clubs": "16",
            "players": "475",
            "marketValue": "€175.30m",
        },
        {
            "id": "BCP2",
            "name": "Campeonato Paulista - Troféu Independência",
            "country": "Brazil",
            "continent": "CONMEBOL",
            "clubs": "6",
            "players": "187",
            "marketValue": "€24.20m",
        },
        {
            "id": "PT3A",
            "name": "Liga 3",
            "country": "Portugal",
            "continent": "UEFA",
            "clubs": "20",
            "players": "568",
            "marketValue": "€19.65m",
        },
        {"id": "POSB", "name": "Serie B Play-off", "country": "Italy"},
        {"id": "ECPE", "name": "Serie A Primera Etapa", "country": "Ecuador"},
    ]

    assert result == expected
