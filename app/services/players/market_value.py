import json
import re
from dataclasses import dataclass, field
from typing import Optional
from xml.etree import ElementTree

from bs4 import ResultSet
from lxml import etree

from app.utils.utils import request_url_bsoup, zip_lists_into_dict
from app.utils.xpath import MarketValue


@dataclass
class TransfermarktPlayerMarketValue:
    player_id: str
    player_marketvalue: dict = field(default_factory=lambda: {"type": "player_marketvalue"})

    def get_player_market_value(self):
        self._request_marketvalue_page()
        self._parse_marketvalue_history()

        self.player_marketvalue["url"] = self._get_text_by_xpath(MarketValue.Players.MARKET_VALUE_URL)
        self.player_marketvalue["player_id"] = self.player_id
        self.player_marketvalue["current"] = "".join(
            self._get_list_by_xpath(MarketValue.Players.CURRENT_VALUE_AND_UPDATED)[:-1]
        )
        self.player_marketvalue["last_update"] = (
            self._get_list_by_xpath(MarketValue.Players.CURRENT_VALUE_AND_UPDATED)[-1].split(":")[-1].strip()
        )
        self.player_marketvalue["ranking"] = zip_lists_into_dict(
            self._get_list_by_xpath(MarketValue.Players.RANKINGS_NAMES),
            self._get_list_by_xpath(MarketValue.Players.RANKINGS_POSITIONS),
        )
        self.player_marketvalue["history"] = self.marketvalue_history

        return self.player_marketvalue

    def _request_marketvalue_page(self) -> None:
        marketvalue_url: str = f"https://www.transfermarkt.com/-/marktwertverlauf/spieler/{self.player_id}"
        self.marketvalue_bsoup = request_url_bsoup(url=marketvalue_url)
        self.marketvalue_page = etree.HTML(str(self.marketvalue_bsoup))

    def _get_text_by_xpath(self, xpath: str) -> Optional[str]:
        element: ElementTree = self.marketvalue_page.xpath(xpath)

        if element:
            return self.marketvalue_page.xpath(xpath)[0].strip().replace("\xa0", "")
        else:
            return None

    def _get_list_by_xpath(self, xpath: str) -> list:
        elements: list = self.marketvalue_page.xpath(xpath)
        elements_valid: list = [e.strip() for e in elements if e.strip()]

        return elements_valid

    def _parse_marketvalue_history(self):
        pages: ResultSet = self.marketvalue_bsoup.findAll("script", type="text/javascript")
        highcharts_page: list = [page for page in pages if str(page).__contains__("Highcharts.Chart")]

        data: str = (
            re.search("data':(.*?)}],'", str(highcharts_page))
            .group(1)
            .replace("\\x27", "`")
            .encode("raw_unicode_escape")
            .decode("unicode_escape")
            .replace("'", '"')
        )

        all_data: list = json.loads(data)
        for entry in all_data:
            entry["date"] = entry.pop("datum_mw")
            entry["club_name"] = entry.pop("verein")
            entry["value"] = entry.pop("mw")

        self.marketvalue_history: list = [
            {key: entry[key] for key in entry if key in ["date", "age", "club_name", "value"]} for entry in all_data
        ]
