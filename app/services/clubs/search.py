from dataclasses import dataclass
from xml.etree import ElementTree

from fastapi import HTTPException

from app.services.commons.search import TransfermarktSearch
from app.utils.utils import extract_from_url, get_list_by_xpath
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubSearch(TransfermarktSearch):
    def search_clubs(self):
        self.result_clubs: ElementTree = self.page.xpath(Clubs.Search.RESULT)

        self._check_club_found()

        clubs_names: list = get_list_by_xpath(self, Clubs.Search.NAMES)
        clubs_urls: list = get_list_by_xpath(self, Clubs.Search.URLS)
        clubs_countries: list = get_list_by_xpath(self, Clubs.Search.COUNTRIES)
        clubs_squads: list = get_list_by_xpath(self, Clubs.Search.SQUADS)
        clubs_market_values: list = get_list_by_xpath(self, Clubs.Search.MARKET_VALUES)
        clubs_ids: list = [extract_from_url(url) for url in clubs_urls]

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

    def _check_club_found(self) -> None:
        if not self.result_clubs:
            raise HTTPException(status_code=404, detail=f"Club Search not found for name: {self.query}")
        else:
            self.page = self.result_clubs[0]
