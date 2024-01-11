from datetime import datetime

import pytest
from schema import And, Schema

from app.services.players.search import TransfermarktPlayerSearch


def test_players_search_empty(len_greater_than_0, len_equal_to_0):
    tfmkt = TransfermarktPlayerSearch(query="0")
    result = tfmkt.search_players()

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


@pytest.mark.parametrize("query,page_number", [("Messi", 1), ("Ronaldo", 2)])
def test_players_search(query, page_number, len_greater_than_0, regex_integer, regex_market_value):
    tfmkt = TransfermarktPlayerSearch(query=query, page_number=page_number)
    result = tfmkt.search_players()

    expected_schema = Schema(
        {
            "query": query,
            "pageNumber": page_number,
            "lastPageNumber": And(int, lambda x: x > 1),
            "results": [
                {
                    "id": And(str, len_greater_than_0, regex_integer),
                    "name": And(str, len_greater_than_0),
                    "position": And(str, len_greater_than_0),
                    "club": {
                        "id": And(str, len_greater_than_0, regex_integer),
                        "name": And(str, len_greater_than_0),
                    },
                    "age": And(str, len_greater_than_0, regex_integer),
                    "nationalities": And(list, len_greater_than_0),
                    "marketValue": And(str, len_greater_than_0, regex_market_value),
                },
            ],
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
