from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import (
    clean_response,
    extract_from_url,
    safe_split,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerTransfers(TransfermarktBase):
    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/transfers/spieler/{player_id}"

    def __post_init__(self):
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.NAME)

    def __parse_player_transfers_history(self) -> list:
        urls = self.get_list_by_xpath(Players.Transfers.TRANSFERS_URLS)
        seasons = self.get_list_by_xpath(Players.Transfers.SEASONS)
        dates = self.get_list_by_xpath(Players.Transfers.DATES)
        old_clubs_urls = self.get_list_by_xpath(Players.Transfers.OLD_CLUBS_URLS)
        old_clubs_names = self.get_list_by_xpath(Players.Transfers.OLD_CLUBS_NAMES)
        new_clubs_urls = self.get_list_by_xpath(Players.Transfers.NEW_CLUBS_URLS)
        new_clubs_names = self.get_list_by_xpath(Players.Transfers.NEW_CLUBS_NAMES)
        market_values = self.get_list_by_xpath(Players.Transfers.MARKET_VALUES)
        fees = self.get_list_by_xpath(Players.Transfers.FEES)

        ids = [extract_from_url(url, "transfer_id") for url in urls]
        old_clubs_ids = [extract_from_url(url) for url in old_clubs_urls]
        new_clubs_ids = [extract_from_url(url) for url in new_clubs_urls]

        return [
            {
                "id": idx,
                "seasonID": season,
                "date": date,
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
                old_clubs_ids,
                old_clubs_names,
                new_clubs_ids,
                new_clubs_names,
                market_values,
                fees,
            )
        ]

    def get_player_transfers(self) -> dict:
        self.response["id"] = self.player_id
        self.response["transfers"] = self.__parse_player_transfers_history()
        self.response["youthClubs"] = safe_split(self.get_text_by_xpath(Players.Transfers.YOUTH_CLUBS), ",")
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
