import json
import re
from dataclasses import dataclass, field

from bs4 import ResultSet

from app.utils.utils import (
    convert_bsoup_to_page,
    get_list_by_xpath,
    get_text_by_xpath,
    remove_str,
    request_url_bsoup,
    zip_lists_into_dict,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerMarketValue:
    player_id: str
    player_marketvalue: dict = field(default_factory=lambda: {})

    def get_player_market_value(self) -> dict:
        self._request_marketvalue_page()

        self.player_marketvalue["id"] = self.player_id
        self.player_marketvalue["playerName"] = get_text_by_xpath(self, Players.Profile.NAME)
        self.player_marketvalue["marketValue"] = get_text_by_xpath(self, Players.MarketValue.CURRENT, join_str="")
        self.player_marketvalue["marketValueHistory"] = self._parse_marketvalue_history()
        self.player_marketvalue["ranking"] = zip_lists_into_dict(
            get_list_by_xpath(self, Players.MarketValue.RANKINGS_NAMES),
            get_list_by_xpath(self, Players.MarketValue.RANKINGS_POSITIONS),
        )
        self.player_marketvalue["lastUpdate"] = remove_str(
            get_text_by_xpath(self, Players.MarketValue.UPDATED), ["Last", "update", ":"]
        )

        return self.player_marketvalue

    def _request_marketvalue_page(self) -> None:
        marketvalue_url: str = f"https://www.transfermarkt.com/-/marktwertverlauf/spieler/{self.player_id}"
        self.bsoup = request_url_bsoup(url=marketvalue_url)
        self.page = convert_bsoup_to_page(self.bsoup)

    def _parse_marketvalue_history(self) -> list:
        pages: ResultSet = self.bsoup.findAll("script", type="text/javascript")
        page_highcharts: list = [page for page in pages if str(page).__contains__("Highcharts.Chart")]

        if (not pages) or (not page_highcharts):
            return []

        data: str = (
            re.search("data':(.*?)}],'", str(page_highcharts))
            .group(1)
            .replace("\\x27", "`")
            .encode("raw_unicode_escape")
            .decode("unicode_escape")
            .replace("'", '"')
        )

        all_data: list = json.loads(data)
        for entry in all_data:
            entry["date"] = entry.pop("datum_mw")
            entry["clubID"] = re.search(r"(?P<club_id>\d+)", entry["marker"]["symbol"]).groupdict().get("club_id")
            entry["clubName"] = entry.pop("verein")
            entry["value"] = entry.pop("mw")

        return [
            {key: entry[key] for key in entry if key in ["date", "age", "club_id", "club_name", "value"]}
            for entry in all_data
        ]
