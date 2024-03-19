from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import clean_response, extract_from_url, to_camel_case, zip_lists_into_dict
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerJerseyNumbers(TransfermarktBase):
    """
    A class for retrieving and parsing the players jersey numbers from Transfermarkt.

    Args:
        player_id (str): The unique identifier of the player.
        URL (str): The URL template for the player's stats page on Transfermarkt.
    """

    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/rueckennummern/spieler/{player_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktJerseyNumbers class."""
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.URL)

    def __parse_player_jersey_numbers(self) -> list:
        """
        Parse and extract player jersey numbers data from the Transfermarkt player stats page.

        Returns:
            list: A list of dictionaries where each dictionary represents the jersey number for a specific season/club.
            Each dictionary includes keys for seasons, clubs and jersey numbers for the player.
        """
        headers = to_camel_case(
            ["Season", "Club", "Jersey number"] + self.get_list_by_xpath(Players.JerseyNumbers.HEADERS),
        )

        seasons = self.get_list_by_xpath(Players.JerseyNumbers.SEASONS)
        clubs_urls = self.get_list_by_xpath(Players.JerseyNumbers.CLUBS_URLS)
        clubs_ids = [extract_from_url(url) for url in clubs_urls]
        jerseynumbers = self.get_list_by_xpath(Players.JerseyNumbers.DATA)
        data = [[season, club_id, number] for season, club_id, number in list(zip(seasons, clubs_ids, jerseynumbers))]

        return [zip_lists_into_dict(headers, stat) for stat in data]

    def get_player_jersey_numbers(self) -> dict:
        """
        Retrieve and parse player jersey numbers data for the specified player from Transfermarkt.

        Returns:
            dict: A dictionary containing the player's unique identifier, parsed player jersey numbers, and
            the timestamp of when the data was last updated.
        """
        self.response["id"] = self.player_id
        self.response["jerseyNumbers"] = self.__parse_player_jersey_numbers()
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
