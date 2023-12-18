from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import clean_response, extract_from_url, to_camel_case, zip_lists_into_dict
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerStats(TransfermarktBase):
    """
    A class for retrieving and parsing the players stats from Transfermarkt.

    Args:
        player_id (str): The unique identifier of the player.
        URL (str): The URL template for the player's stats page on Transfermarkt.
    """

    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/leistungsdatendetails/spieler/{player_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktPlayerStats class."""
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.URL)

    def __parse_player_stats(self) -> list:
        """
        Parse and extract player statistics data from the Transfermarkt player stats page.

        Returns:
            list: A list of dictionaries where each dictionary represents the statistics for a specific competition.
                Each dictionary includes keys for competition ID, club ID, season ID, competition name, and various
                statistical values for the player.
        """
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
        """
        Retrieve and parse player statistics data for the specified player from Transfermarkt.

        Returns:
            dict: A dictionary containing the player's unique identifier, parsed player statistics, and the timestamp of
            when the data was last updated.
        """
        self.response["id"] = self.player_id
        self.response["stats"] = self.__parse_player_stats()
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
