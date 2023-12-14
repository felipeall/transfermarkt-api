from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionSearch(TransfermarktBase):
    """
    A class for searching football competitions on Transfermarkt and retrieving search results.

    Args:
        query (str): The search query for finding football clubs.
        URL (str): The URL template for the search query.
        page_number (int): The page number of search results (default is 1).
    """

    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Wettbewerb_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self) -> None:
        """Initialize the TransfermarktCompetitionSearch class."""
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()

    def __parse_search_results(self) -> list:
        """
        Parse and retrieve the search results for football competitions from Transfermarkt.

        Returns:
            list: A list of dictionaries, each containing details of a football competition,
                including its unique identifier, name, country, associated clubs, number of players,
                total market value, mean market value, and continent.
        """
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

    def search_competitions(self) -> dict:
        """
        Perform a search for football competitions and retrieve the search results.

        Returns:
            dict: A dictionary containing search results, including competition details.
        """
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number(Competitions.Search.BASE)
        self.response["results"] = self.__parse_search_results()
        self.response["updatedAt"] = datetime.now()

        return self.response
