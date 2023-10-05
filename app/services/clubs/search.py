from dataclasses import dataclass

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubSearch(TransfermarktBase):
    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Verein_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self):
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()

    def __parse_search_results(self) -> list:
        clubs_names = self.get_list_by_xpath(Clubs.Search.NAMES)
        clubs_urls = self.get_list_by_xpath(Clubs.Search.URLS)
        clubs_countries = self.get_list_by_xpath(Clubs.Search.COUNTRIES)
        clubs_squads = self.get_list_by_xpath(Clubs.Search.SQUADS)
        clubs_market_values = self.get_list_by_xpath(Clubs.Search.MARKET_VALUES)
        clubs_ids = [extract_from_url(url) for url in clubs_urls]

        return [
            {
                "id": idx,
                "url": url,
                "name": name,
                "country": country,
                "squad": squad,
                "marketValue": market_value,
            }
            for idx, url, name, country, squad, market_value in zip(
                clubs_ids,
                clubs_urls,
                clubs_names,
                clubs_countries,
                clubs_squads,
                clubs_market_values,
            )
        ]

    def search_clubs(self) -> dict:
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_search_last_page_number(Clubs.Search.BASE)
        self.response["results"] = self.__parse_search_results()

        return self.response
