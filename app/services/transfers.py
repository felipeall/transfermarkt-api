from dataclasses import dataclass, field
from datetime import datetime

from app.utils.utils import (
    extract_code_from_tfmkt_url,
    extract_id_from_tfmkt_url,
    request_url_page,
)
from app.utils.xpath import Transfers


@dataclass
class TransfermarktPlayerTransfers:
    player_code: str
    player_id: str
    player_transfers: dict = field(default_factory=lambda: {"type": "player_transfers"})

    def get_player_transfers(self) -> dict:
        self._request_player_transfers_page()

        self.player_transfers["player_code"] = self.player_code
        self.player_transfers["player_id"] = self.player_id
        self.player_transfers["history"] = self._parse_player_transfers_history()
        self.player_transfers["youth_clubs"] = self._get_list_by_xpath(Transfers.Players.YOUTH_CLUBS)
        self.player_transfers["last_update"] = datetime.now()

        return self.player_transfers

    def _request_player_transfers_page(self) -> None:
        player_transfers_url = f"https://www.transfermarkt.com/{self.player_code}/transfers/spieler/{self.player_id}"
        self.player_transfers_page = request_url_page(url=player_transfers_url)

    def _get_list_by_xpath(self, xpath: str) -> list:
        elements: list = self.player_transfers_page.xpath(xpath)
        elements_valid: list = [e.strip().split(",")[0] for e in elements if e.strip()]

        return elements_valid

    def _parse_player_transfers_history(self) -> list:
        urls: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_URLS)
        seasons: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_SEASONS)
        dates: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_DATES)
        from_clubs_names: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_CLUBS_NAMES)[::2]
        from_clubs_urls: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_FROM_CLUBS_URLS)
        to_clubs_names: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_CLUBS_NAMES)[1::2]
        to_clubs_urls: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_TO_CLUBS_URLS)
        market_values: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_MARKET_VALUES)
        fees: list = self._get_list_by_xpath(Transfers.Players.TRANSFERS_FEES)

        ids: list = [extract_id_from_tfmkt_url(url) for url in urls]
        from_clubs_codes: list = [extract_code_from_tfmkt_url(url) for url in from_clubs_urls]
        from_clubs_ids: list = [extract_id_from_tfmkt_url(url) for url in from_clubs_urls]
        to_clubs_codes: list = [extract_code_from_tfmkt_url(url) for url in to_clubs_urls]
        to_clubs_ids: list = [extract_id_from_tfmkt_url(url) for url in to_clubs_urls]

        return [
            {
                "id": idx,
                "season": season,
                "date": date,
                "from": {
                    "club_code": from_club_code,
                    "club_id": from_club_id,
                    "club_name": from_club_name,
                },
                "to": {
                    "club_code": to_club_code,
                    "club_id": to_club_id,
                    "club_name": to_club_name,
                },
                "market_value": market_value,
                "fee": fee,
            }
            for idx, season, date, from_club_code, from_club_id, from_club_name, to_club_code, to_club_id, to_club_name, market_value, fee in zip(
                ids,
                seasons,
                dates,
                from_clubs_codes,
                from_clubs_ids,
                from_clubs_names,
                to_clubs_codes,
                to_clubs_ids,
                to_clubs_names,
                market_values,
                fees,
            )
        ]
