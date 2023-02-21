from dataclasses import dataclass, field
from datetime import datetime

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    request_url_page,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerTransfers:
    player_id: str
    player_transfers: dict = field(default_factory=lambda: {"type": "player_transfers"})

    def get_player_transfers(self) -> dict:
        self._request_player_transfers_page()

        self.player_transfers["url"] = get_text_by_xpath(self, Players.Transfers.PLAYER_URL)
        self.player_transfers["player_id"] = self.player_id
        self.player_transfers["player_name"] = " ".join(get_list_by_xpath(self, Players.Profile.NAME)[1:])
        self.player_transfers["history"] = self._parse_player_transfers_history()
        self.player_transfers["youth_clubs"] = get_list_by_xpath(self, Players.Transfers.YOUTH_CLUBS)
        self.player_transfers["last_update"] = datetime.now()

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
                "id": idx,
                "season": season,
                "date": date,
                "from": {
                    "club_id": from_club_id,
                    "club_name": from_club_name,
                },
                "to": {
                    "club_id": to_club_id,
                    "club_name": to_club_name,
                },
                "market_value": market_value,
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
