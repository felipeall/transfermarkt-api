from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import (
    clean_response,
    extract_from_url,
    to_camel_case,
    zip_lists_into_dict,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerStats(TransfermarktBase):
    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/leistungsdatendetails/spieler/{player_id}"

    def __post_init__(self):
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.URL)

    def __parse_player_stats(self) -> list:
        rows = self.page.xpath(Players.Stats.ROWS)
        headers = to_camel_case(
            ["Competition id", "Club id", "Season id", "Competition name"]
            + self.get_list_by_xpath(Players.Stats.HEADERS),
        )

        competitions_urls = self.get_list_by_xpath(Players.Stats.COMPETITIONS_URLS)
        clubs_urls = self.get_list_by_xpath(Players.Stats.CLUBS_URLS)
        competitions_ids = [extract_from_url(url) for url in competitions_urls]
        clubs_ids = [extract_from_url(url) for url in clubs_urls]
        stats = [
            [item for text in row.xpath(Players.Stats.DATA) if text != "\xa0" for item in text.split("\xa0/\xa0")][1:]
            for row in rows
        ]
        data = [
            [comp_url, club_url] + stats for comp_url, club_url, stats in list(zip(competitions_ids, clubs_ids, stats))
        ]

        return [zip_lists_into_dict(headers, stat) for stat in data]

    def get_player_stats(self) -> dict:
        self.response["id"] = self.player_id
        self.response["stats"] = self.__parse_player_stats()
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
