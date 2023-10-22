from datetime import datetime

import pytest
from schema import And, Schema

from app.services.clubs.search import TransfermarktClubSearch


def test_search_clubs_empty(len_greater_than_0, len_equal_to_0):
    tfmkt = TransfermarktClubSearch(query="0")
    result = tfmkt.search_clubs()

    expected_schema = Schema(
        {
            "query": And(str, len_greater_than_0),
            "pageNumber": 1,
            "lastPageNumber": 1,
            "results": And(list, len_equal_to_0),
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)


@pytest.mark.parametrize("query,page_number", [("gremio", 1), ("atletico", 2)])
def test_search_clubs(query, page_number, regex_club_url, regex_integer, regex_market_value, len_greater_than_0):
    tfmkt = TransfermarktClubSearch(query=query, page_number=page_number)
    result = tfmkt.search_clubs()

    expected_schema = Schema(
        {
            "query": query,
            "pageNumber": page_number,
            "lastPageNumber": And(int, lambda x: x > 1),
            "results": [
                {
                    "id": And(str, len_greater_than_0, regex_integer),
                    "url": And(str, len_greater_than_0, regex_club_url),
                    "name": And(str, len_greater_than_0),
                    "country": And(str, len_greater_than_0),
                    "squad": And(str, len_greater_than_0, regex_integer),
                    "marketValue": And(str, len_greater_than_0, regex_market_value),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
