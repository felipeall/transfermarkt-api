from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree

from fastapi import HTTPException

from app.utils.utils import extract_from_url, get_list_by_xpath, request_url_page
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubSearch:
    query: str
    page_number: Optional[int] = 1

    def __post_init__(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}&Verein_page={self.page_number}"
        self.page = request_url_page(url=search_url)
        self._check_club_found()

    def search_clubs(self):
        clubs_names: list = get_list_by_xpath(self, Clubs.Search.NAMES)
        clubs_urls: list = get_list_by_xpath(self, Clubs.Search.URLS)
        clubs_countries: list = get_list_by_xpath(self, Clubs.Search.COUNTRIES)
        clubs_squads: list = get_list_by_xpath(self, Clubs.Search.SQUADS)
        clubs_market_values: list = get_list_by_xpath(self, Clubs.Search.MARKET_VALUES)
        clubs_ids: list = [extract_from_url(url) for url in clubs_urls]

        return {
            "query": self.query,
            "pageNumber": self.page_number,
            "lastPageNumber": self._get_last_page_number(),
            "results": [
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
            ],
        }

    def _check_club_found(self) -> None:
        result_clubs: ElementTree = self.page.xpath(Clubs.Search.RESULT)
        if not result_clubs:
            raise HTTPException(status_code=404, detail=f"Club Search not found for name: {self.query}")
        else:
            self.page = result_clubs[0]

    def _get_last_page_number(self) -> int:
        url_page_number_last: list = self.page.xpath(Clubs.Search.PAGE_NUMBER_LAST)
        url_page_number_active: list = self.page.xpath(Clubs.Search.PAGE_NUMBER_ACTIVE)

        if url_page_number_last:
            last_page_number = int(url_page_number_last[0].split("=")[-1])
        else:
            last_page_number = int(url_page_number_active[0].split("=")[-1])

        return last_page_number
