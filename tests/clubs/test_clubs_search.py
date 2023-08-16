import pytest
from fastapi import HTTPException

from app.services.clubs.search import TransfermarktClubSearch


def test_clubs_search_0():
    with pytest.raises(HTTPException):
        TransfermarktClubSearch(query="0")


def test_clubs_search_gremio():
    tfmkt = TransfermarktClubSearch(query="gremio")
    result = tfmkt.search_clubs()

    expected = {
        "query": "gremio",
        "pageNumber": 1,
        "lastPageNumber": 4,
        "results": [
            {
                "id": "210",
                "url": "/gremio-porto-alegre/startseite/verein/210",
                "name": "Grêmio Foot-Ball Porto Alegrense",
                "country": "Brazil",
                "squad": "33",
                "marketValue": "€65.45m",
            },
            {
                "id": "37474",
                "url": "/gremio-novorizontino-sp-/startseite/verein/37474",
                "name": "Grêmio Novorizontino",
                "country": "Brazil",
                "squad": "33",
                "marketValue": "€10.45m",
            },
            {
                "id": "10560",
                "url": "/gremio-esportivo-brasil-rs-/startseite/verein/10560",
                "name": "Grêmio Esportivo Brasil (RS)",
                "country": "Brazil",
                "squad": "24",
                "marketValue": "€1.00m",
            },
            {
                "id": "14704",
                "url": "/gremio-porto-alegre-b/startseite/verein/14704",
                "name": "Grêmio Foot-Ball Porto Alegrense B (-2022)",
                "country": "Brazil",
                "squad": "2",
                "marketValue": "€950k",
            },
            {
                "id": "12690",
                "url": "/gremio-porto-alegre-u20/startseite/verein/12690",
                "name": "Grêmio FBPA U20",
                "country": "Brazil",
                "squad": "53",
                "marketValue": "€500k",
            },
            {
                "id": "16083",
                "url": "/gremio-osasco-audax-sp-/startseite/verein/16083",
                "name": "Grêmio Osasco Audax (SP)",
                "country": "Brazil",
                "squad": "11",
                "marketValue": "€450k",
            },
            {
                "id": "36166",
                "url": "/gremio-desportivo-prudente-sp-/startseite/verein/36166",
                "name": "Grêmio Desportivo Prudente (SP)",
                "country": "Brazil",
                "squad": "24",
                "marketValue": "€200k",
            },
            {
                "id": "76417",
                "url": "/gremio-desportivo-sao-carlense/startseite/verein/76417",
                "name": "Grêmio Desportivo São-Carlense (SP)",
                "country": "Brazil",
                "squad": "20",
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
                "squad": "11",
                "marketValue": "€75k",
            },
        ],
    }

    assert result == expected
