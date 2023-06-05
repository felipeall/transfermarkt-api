import pytest
from fastapi import HTTPException

from app.services.clubs.search import TransfermarktClubSearch


def test_clubs_search_0():
    tfmkt = TransfermarktClubSearch(query="0")

    with pytest.raises(HTTPException):
        tfmkt.search_clubs()


def test_clubs_search_gremio():
    tfmkt = TransfermarktClubSearch(query="gremio")
    result = tfmkt.search_clubs()

    expected = [
        {
            "id": "210",
            "url": "/gremio-porto-alegre/startseite/verein/210",
            "name": "Grêmio Foot-Ball Porto Alegrense",
            "country": "Brazil",
            "squad": "36",
            "marketValue": "€54.10m",
        },
        {
            "id": "37474",
            "url": "/gremio-novorizontino-sp-/startseite/verein/37474",
            "name": "Grêmio Novorizontino",
            "country": "Brazil",
            "squad": "33",
            "marketValue": "€9.43m",
        },
        {
            "id": "10560",
            "url": "/gremio-esportivo-brasil-rs-/startseite/verein/10560",
            "name": "Grêmio Esportivo Brasil (RS)",
            "country": "Brazil",
            "squad": "23",
            "marketValue": "€1.00m",
        },
        {
            "id": "36166",
            "url": "/gremio-desportivo-prudente-sp-/startseite/verein/36166",
            "name": "Grêmio Desportivo Prudente (SP)",
            "country": "Brazil",
            "squad": "17",
            "marketValue": "€650k",
        },
        {
            "id": "14704",
            "url": "/gremio-porto-alegre-b/startseite/verein/14704",
            "name": "Grêmio Foot-Ball Porto Alegrense B (-2022)",
            "country": "Brazil",
            "squad": "1",
            "marketValue": "€600k",
        },
        {
            "id": "16083",
            "url": "/gremio-osasco-audax-sp-/startseite/verein/16083",
            "name": "Grêmio Osasco Audax (SP)",
            "country": "Brazil",
            "squad": "17",
            "marketValue": "€450k",
        },
        {
            "id": "10117",
            "url": "/gremio-esportivo-juventus-sc-/startseite/verein/10117",
            "name": "Grêmio Esportivo Juventus (SC)",
            "country": "Brazil",
            "squad": "25",
            "marketValue": "€200k",
        },
        {
            "id": "76417",
            "url": "/gremio-desportivo-sao-carlense/startseite/verein/76417",
            "name": "Grêmio Desportivo São-Carlense (SP)",
            "country": "Brazil",
            "squad": "18",
            "marketValue": "€125k",
        },
        {
            "id": "96879",
            "url": "/gremio-desportivo-sao-carlense-sp-u20/startseite/verein/96879",
            "name": "Grêmio Desportivo São-Carlense (SP) U20",
            "country": "Brazil",
            "squad": "22",
            "marketValue": "€100k",
        },
        {
            "id": "94170",
            "url": "/gremio-pague-menos/startseite/verein/94170",
            "name": "Grêmio Pague Menos",
            "country": "Brazil",
            "squad": "12",
            "marketValue": "€75k",
        },
    ]
    assert result == expected
