from dataclasses import dataclass, field
from datetime import datetime

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    request_url_page,
    safe_split,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerTransfers:
    player_id: str
    player_transfers: dict = field(default_factory=lambda: {})

    def get_player_transfers(self) -> dict:
        self._request_player_transfers_page()

        self.player_transfers["id"] = self.player_id
        self.player_transfers["name"] = get_text_by_xpath(self, Players.Profile.NAME)
        self.player_transfers["history"] = self._parse_player_transfers_history()
        self.player_transfers["youthClubs"] = safe_split(get_text_by_xpath(self, Players.Transfers.YOUTH_CLUBS), ",")
        self.player_transfers["lastUpdate"] = datetime.now()

        return clean_response(self.player_transfers)

    def _request_player_transfers_page(self) -> None:
        player_transfers_url = f"https://www.transfermarkt.com/-/transfers/spieler/{self.player_id}"
        self.page = request_url_page(url=player_transfers_url)

    def _parse_player_transfers_history(self) -> list:
        urls: list = get_list_by_xpath(self, Players.Transfers.TRANSFERS_URLS)
        seasons: list = get_list_by_xpath(self, Players.Transfers.SEASONS)
        dates: list = get_list_by_xpath(self, Players.Transfers.DATES)
        from_clubs_names: list = get_list_by_xpath(self, Players.Transfers.CLUBS_NAMES)[::2]
        from_clubs_urls: list = get_list_by_xpath(self, Players.Transfers.FROM_CLUBS_URLS)
        to_clubs_names: list = get_list_by_xpath(self, Players.Transfers.CLUBS_NAMES)[1::2]
        to_clubs_urls: list = get_list_by_xpath(self, Players.Transfers.TO_CLUBS_URLS)
        market_values: list = get_list_by_xpath(self, Players.Transfers.MARKET_VALUES)
        fees: list = get_list_by_xpath(self, Players.Transfers.FEES)

        ids: list = [extract_from_url(url, "transfer_id") for url in urls]
        from_clubs_ids: list = [extract_from_url(url) for url in from_clubs_urls]
        to_clubs_ids: list = [extract_from_url(url) for url in to_clubs_urls]

        return [
            {
                "transferID": idx,
                "transferSeason": season,
                "transferDate": date,
                "oldClubID": from_club_id,
                "oldClubName": from_club_name,
                "newClubID": to_club_id,
                "newClubName": to_club_name,
                "marketValue": market_value,
                "fee": fee,
            }
            for idx, season, date, from_club_id, from_club_name, to_club_id, to_club_name, market_value, fee in zip(
                ids,
                seasons,
                dates,
                from_clubs_ids,
                from_clubs_names,
                to_clubs_ids,
                to_clubs_names,
                market_values,
                fees,
            )
        ]
