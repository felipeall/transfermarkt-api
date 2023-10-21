from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_CHART_CLUB_ID
from app.utils.utils import extract_from_url, safe_regex
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerSearch(TransfermarktBase):
    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Spieler_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self):
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Search.FOUND)

    def __parse_search_results(self) -> list:
        idx = [extract_from_url(url) for url in self.get_list_by_xpath(Players.Search.URL)]
        name = self.get_list_by_xpath(Players.Search.NAME)
        position = self.get_list_by_xpath(Players.Search.POSITION)
        club_name = self.get_list_by_xpath(Players.Search.CLUB_NAME)
        club_id = [
            safe_regex(img, REGEX_CHART_CLUB_ID, "club_id") for img in self.get_list_by_xpath(Players.Search.CLUB_IMAGE)
        ]
        age = self.get_list_by_xpath(Players.Search.AGE)
        nationality = self.get_list_by_xpath(Players.Search.NATIONALITY)
        market_value = self.get_list_by_xpath(Players.Search.MARKET_VALUE)

        return [
            {
                "id": idx,
                "name": name,
                "position": position,
                "club": {
                    "id": club_id,
                    "name": club_name,
                },
                "age": age,
                "nationality": nationality,
                "marketValue": market_value,
            }
            for idx, name, club_id, club_name, position, age, nationality, market_value in zip(
                idx,
                name,
                club_id,
                club_name,
                position,
                age,
                nationality,
                market_value,
            )
        ]

    def search_players(self) -> dict:
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_search_last_page_number(Players.Search.BASE)
        self.response["results"] = self.__parse_search_results()
        self.response["updatedAt"] = datetime.now()

        return self.response
