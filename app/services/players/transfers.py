from dataclasses import dataclass
from bs4 import BeautifulSoup
import re
from typing import Tuple

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url, safe_split
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerTransfers(TransfermarktBase):
    """
    A class for retrieving and parsing the player's transfer history and youth club details from Transfermarkt.

    Args:
        player_id (str): The unique identifier of the player.
        URL (str): The URL template for the player's transfers page on Transfermarkt.
    """

    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/transfers/spieler/{player_id}"
    URL_TRANSFERS: str = "https://www.transfermarkt.com/ceapi/transferHistory/list/{player_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktPlayerTransfers class."""
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.NAME)
        self.transfer_history = self.make_request(url=self.URL_TRANSFERS.format(player_id=self.player_id))

    def __clean_html_value(self, value: str) -> Tuple[str, str]:
        """
        Clean HTML tags from a string value and extract just the currency value or preserve special text values.
        Also determine the transfer type based on the fee text.
        
        Args:
            value (str): The string value that may contain HTML tags.
            
        Returns:
            Tuple[str, str]: A tuple containing (cleaned_fee_value, transfer_type)
        """
        if not value or not isinstance(value, str):
            return value, "permanent"
            
        soup = BeautifulSoup(value, 'html.parser')
        text = soup.get_text().strip()
        
        if "end of loan" in text.lower():
            return "End of loan", "end_of_loan"
            
        if "loan transfer" in text.lower() and not any(char.isdigit() for char in text):
            return "loan transfer", "loan"
        
        if "fee" in text.lower():
            currency_match = re.search(r'(€\d+(?:\.\d+)?[km]?)', text)
            if currency_match:
                if "loan" in text.lower():
                    return currency_match.group(1), "loan"
                return currency_match.group(1), "permanent"
                
            number_match = re.search(r'(\d+(?:\.\d+)?[km]?)', text)
            if number_match:
                if "loan" in text.lower():
                    return number_match.group(1), "loan"
                return number_match.group(1), "permanent"
                
            if "loan" in text.lower() and not any(char.isdigit() for char in text):
                return "€0", "loan"
        
        if "free transfer" in text.lower() or text == "-":
            return "€0", "free_transfer"
            
        return text, "permanent"

    def __parse_player_transfer_history(self) -> list:
        """
        Parse and retrieve the transfer history of the specified player from Transfermarkt,
        including the unique identifier of each transfer, source club information (ID and name),
        destination club information (ID and name), transfer date, upcoming status, season, market
        value at the time of transfer, and transfer fee.

        Returns:
            list: A list of dictionaries, each containing details of the player's transfer history,
        """
        transfers = self.transfer_history.json().get("transfers")

        return [
            {
                "id": extract_from_url(transfer["url"], "transfer_id"),
                "clubFrom": {
                    "id": extract_from_url(transfer["from"]["href"]),
                    "name": transfer["from"]["clubName"],
                },
                "clubTo": {
                    "id": extract_from_url(transfer["to"]["href"]),
                    "name": transfer["to"]["clubName"],
                },
                "date": transfer["date"],
                "upcoming": transfer["upcoming"],
                "season": transfer["season"],
                "marketValue": transfer["marketValue"],
                **self.__process_fee_and_type(transfer["fee"]),
            }
            for transfer in transfers
        ]
        
    def __process_fee_and_type(self, fee_value: str) -> dict:
        """
        Process the fee value and determine the transfer type.
        
        Args:
            fee_value (str): The raw fee value from the transfer data.
            
        Returns:
            dict: A dictionary containing the cleaned fee value and transfer type.
        """
        fee, transfer_type = self.__clean_html_value(fee_value)
        return {
            "fee": fee,
            "transferType": transfer_type
        }

    def get_player_transfers(self) -> dict:
        """
        Retrieve and parse the transfer history and youth clubs of the specified player from Transfermarkt.

        Returns:
            dict: A dictionary containing the player's unique identifier, parsed transfer history, youth clubs,
                  and the timestamp of when the data was last updated.
        """
        self.response["id"] = self.player_id
        self.response["transfers"] = self.__parse_player_transfer_history()
        self.response["youthClubs"] = safe_split(self.get_text_by_xpath(Players.Transfers.YOUTH_CLUBS), ",")

        return self.response
