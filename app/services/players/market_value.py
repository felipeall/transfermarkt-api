import json
import re
from dataclasses import dataclass, field

from fastapi import HTTPException

from app.utils.utils import (
    clean_response,
    convert_bsoup_to_page,
    get_list_by_xpath,
    get_text_by_xpath,
    make_request,
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

        self._check_player_found()

        self.player_marketvalue["marketValue"] = get_text_by_xpath(self, Players.MarketValue.CURRENT, join_str="")
        self.player_marketvalue["marketValueHistory"] = self._parse_marketvalue_history()
        self.player_marketvalue["ranking"] = zip_lists_into_dict(
            get_list_by_xpath(self, Players.MarketValue.RANKINGS_NAMES),
            get_list_by_xpath(self, Players.MarketValue.RANKINGS_POSITIONS),
        )
        self.player_marketvalue["lastUpdate"] = remove_str(
            get_text_by_xpath(self, Players.MarketValue.UPDATED),
            ["Last", "update", ":"],
        )

        return clean_response(self.player_marketvalue)

    def _request_marketvalue_page(self) -> None:
        marketvalue_url: str = f"https://www.transfermarkt.com/-/marktwertverlauf/spieler/{self.player_id}"
        self.bsoup = request_url_bsoup(url=marketvalue_url)
        self.page = convert_bsoup_to_page(self.bsoup)

    def _check_player_found(self) -> None:
        if not self.player_marketvalue["playerName"]:
            raise HTTPException(status_code=404, detail=f"Player Market Value not found for id: {self.player_id}")

    def _parse_marketvalue_history(self) -> list:
        response = make_request(f"https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/{self.player_id}")
        data: list = json.loads(response.content).get("list")

        wappen = None
        for entry in data:
            entry["date"] = entry.pop("datum_mw")
            entry["clubName"] = entry.pop("verein")
            entry["value"] = entry.pop("mw")
            if not entry.get("wappen"):
                entry["wappen"] = wappen
            else:
                wappen = entry["wappen"]
            entry["clubID"] = re.search(r"(?P<club_id>\d+)", entry["wappen"]).groupdict().get("club_id")

        return [
            {key: entry[key] for key in entry if key in ["date", "age", "clubID", "clubName", "value"]}
            for entry in data
        ]
