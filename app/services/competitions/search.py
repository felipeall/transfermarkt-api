from dataclasses import dataclass

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionSearch(TransfermarktBase):
    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Wettbewerb_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self):
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()

    def __parse_search_results(self) -> list:
        idx = [extract_from_url(url) for url in self.get_list_by_xpath(Competitions.Search.URLS)]
        name = self.get_list_by_xpath(Competitions.Search.NAMES)
        country = self.get_list_by_xpath(Competitions.Search.COUNTRIES)
        clubs = self.get_list_by_xpath(Competitions.Search.CLUBS)
        players = self.get_list_by_xpath(Competitions.Search.PLAYERS)
        total_market_value = self.get_list_by_xpath(Competitions.Search.TOTAL_MARKET_VALUES)
        mean_market_value = self.get_list_by_xpath(Competitions.Search.MEAN_MARKET_VALUES)
        continent = self.get_list_by_xpath(Competitions.Search.CONTINENTS)

        return [
            {
                "id": idx,
                "name": name,
                "country": country,
                "clubs": clubs,
                "players": players,
                "totalMarketValue": total_market_value,
                "meanMarketValue": mean_market_value,
                "continent": continent,
            }
            for idx, name, country, clubs, players, total_market_value, mean_market_value, continent in zip(
                idx,
                name,
                country,
                clubs,
                players,
                total_market_value,
                mean_market_value,
                continent,
            )
        ]

    def search_competitions(self):
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_search_last_page_number(Competitions.Search.BASE)
        self.response["results"] = self.__parse_search_results()

        return self.response
