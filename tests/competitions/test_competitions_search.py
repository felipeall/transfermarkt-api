from datetime import datetime

import pytest
from schema import And, Schema

from app.services.competitions.search import TransfermarktCompetitionSearch


def test_search_competitions_not_found(len_greater_than_0, len_equal_to_0):
    tfmkt = TransfermarktCompetitionSearch(query="0")
    result = tfmkt.search_competitions()

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


@pytest.mark.parametrize("query,page_number", [("Serie A", 1), ("Liga", 2)])
def test_search_competitions(query, page_number, len_greater_than_0, regex_integer, regex_market_value):
    tfmkt = TransfermarktCompetitionSearch(query=query, page_number=page_number)
    result = tfmkt.search_competitions()

    expected_schema = Schema(
        {
            "query": query,
            "pageNumber": page_number,
            "lastPageNumber": And(int, lambda x: x > 1),
            "results": [
                {
                    "id": And(str, len_greater_than_0),
                    "name": And(str, len_greater_than_0),
                    "country": And(str, len_greater_than_0),
                    "continent": And(str, len_greater_than_0),
                    "clubs": And(str, len_greater_than_0, regex_integer, regex_integer),
                    "players": And(str, len_greater_than_0, regex_integer, regex_integer),
                    "totalMarketValue": And(str, len_greater_than_0, regex_market_value),
                    "meanMarketValue": And(str, len_greater_than_0, regex_market_value),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
