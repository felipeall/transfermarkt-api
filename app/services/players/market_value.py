import json
from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_CHART_CLUB_ID
from app.utils.utils import clean_response, safe_regex, zip_lists_into_dict
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerMarketValue(TransfermarktBase):
    """
    Represents a service for retrieving and parsing the market value history of a football player on Transfermarkt.

    Args:
        player_id (str): The unique identifier of the player.

    Attributes:
        URL (str): The URL to fetch the player's market value data.
        URL_MARKET_VALUE (str): The URL to fetch the player's market value history chart data.
    """

    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/marktwertverlauf/spieler/{player_id}"
    URL_MARKET_VALUE: str = "https://www.transfermarkt.com/ceapi/marketValueDevelopment/graph/{player_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktPlayerMarketValue class."""
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.NAME)
        self.market_value_chart = self.make_request(url=self.URL_MARKET_VALUE.format(player_id=self.player_id))

    def __parse_market_value_history(self) -> list:
        """
        Parse the market value history of a football player from the retrieved data.

        Returns:
            list: A list of dictionaries, where each dictionary represents a data point in the
                player's market value history. Each dictionary contains keys 'date', 'age',
                'clubID', 'clubName', and 'value' with their respective values.
        """
        data = json.loads(self.market_value_chart.content).get("list")

        club_image = None
        for entry in data:
            entry["date"] = entry.pop("datum_mw")
            entry["clubName"] = entry.pop("verein")
            entry["value"] = entry.pop("mw")
            if not entry.get("wappen"):
                entry["wappen"] = club_image
            else:
                club_image = entry["wappen"]
            entry["clubID"] = safe_regex(entry["wappen"], REGEX_CHART_CLUB_ID, "club_id")

        return [
            {key: entry[key] for key in entry if key in ["date", "age", "clubID", "clubName", "value"]}
            for entry in data
        ]

    def get_player_market_value(self) -> dict:
        """
        Retrieve and parse the market value history of a football player.

        Returns:
            dict: A dictionary containing the player's unique identifier, current market value,
                market value history, ranking, and the timestamp of when the data was last updated.
        """
        self.response["id"] = self.player_id
        self.response["marketValue"] = self.get_text_by_xpath(Players.MarketValue.CURRENT, join_str="")
        self.response["marketValueHistory"] = self.__parse_market_value_history()
        self.response["ranking"] = zip_lists_into_dict(
            self.get_list_by_xpath(Players.MarketValue.RANKINGS_NAMES),
            self.get_list_by_xpath(Players.MarketValue.RANKINGS_POSITIONS),
        )
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
