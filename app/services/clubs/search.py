from dataclasses import dataclass
from xml.etree import ElementTree

from app.services.commons.search import TransfermarktSearch
from app.utils.utils import extract_id_from_tfmkt_url, trim
from app.utils.xpath import Search


@dataclass
class TransfermarktClubSearch(TransfermarktSearch):
    result_clubs = None

    def search_clubs(self):
        self.result_clubs: ElementTree = self.search_page.xpath(Search.Clubs.RESULT)

        if not self.result_clubs:
            return None
        else:
            self.result_clubs = self.result_clubs[0]

        clubs_names: list = self._get_list_by_xpath(Search.Clubs.NAMES)
        clubs_urls: list = self._get_list_by_xpath(Search.Clubs.URLS)
        clubs_countries: list = self._get_list_by_xpath(Search.Clubs.COUNTRIES)
        clubs_squads: list = self._get_list_by_xpath(Search.Clubs.SQUADS)
        clubs_market_values: list = self._get_list_by_xpath(Search.Clubs.MARKET_VALUES)
        clubs_ids: list = [extract_id_from_tfmkt_url(url) for url in clubs_urls]

        return [
            {
                "id": idx,
                "url": url,
                "name": name,
                "country": country,
                "squad": squad,
                "market_value": market_value,
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

    def _get_list_by_xpath(self, xpath: str):
        elements: list = self.result_clubs.xpath(xpath)
        elements_valid: list = [trim(e) for e in elements if trim(e)]

        return elements_valid or None
