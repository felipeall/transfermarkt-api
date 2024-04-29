from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_DOB_AGE
from app.utils.utils import clean_response, extract_from_url, safe_regex
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerProfile(TransfermarktBase):
    """
    Represents a service for retrieving and parsing the profile information of a football player on Transfermarkt.

    Args:
        player_id (str): The unique identifier of the player.

    Attributes:
        URL (str): The URL to fetch the player's profile data.
    """

    player_id: str = None
    URL: str = "https://www.transfermarkt.com/-/profil/spieler/{player_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktPlayerProfile class."""
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.URL)

    def get_player_profile(self) -> dict:
        """
        Retrieve and parse the player's profile information, including their personal details,
        club affiliations, market value, agent information, social media links, and more.

        Returns:
            dict: A dictionary containing the player's unique identifier, profile information, and the timestamp of when
                the data was last updated.
        """
        self.response["id"] = self.get_text_by_xpath(Players.Profile.ID)
        self.response["url"] = self.get_text_by_xpath(Players.Profile.URL)
        self.response["name"] = self.get_text_by_xpath(Players.Profile.NAME, join_str=" ")
        self.response["description"] = self.get_text_by_xpath(Players.Profile.DESCRIPTION)
        self.response["fullName"] = self.get_text_by_xpath(Players.Profile.FULL_NAME)
        self.response["nameInHomeCountry"] = self.get_text_by_xpath(Players.Profile.NAME_IN_HOME_COUNTRY)
        self.response["imageURL"] = self.get_text_by_xpath(Players.Profile.IMAGE_URL)
        self.response["dateOfBirth"] = safe_regex(
            self.get_text_by_xpath(Players.Profile.DATE_OF_BIRTH_AGE),
            REGEX_DOB_AGE,
            "dob",
        )
        self.response["placeOfBirth"] = {
            "city": self.get_text_by_xpath(Players.Profile.PLACE_OF_BIRTH_CITY),
            "country": self.get_text_by_xpath(Players.Profile.PLACE_OF_BIRTH_COUNTRY),
        }
        self.response["age"] = safe_regex(
            self.get_text_by_xpath(Players.Profile.DATE_OF_BIRTH_AGE),
            REGEX_DOB_AGE,
            "age",
        )
        self.response["height"] = self.get_text_by_xpath(Players.Profile.HEIGHT)
        self.response["citizenship"] = self.get_list_by_xpath(Players.Profile.CITIZENSHIP)
        self.response["isRetired"] = self.get_text_by_xpath(Players.Profile.RETIRED_SINCE_DATE) is not None
        self.response["retiredSince"] = self.get_text_by_xpath(Players.Profile.RETIRED_SINCE_DATE)
        self.response["position"] = {
            "main": self.get_text_by_xpath(Players.Profile.POSITION_MAIN),
            "other": self.get_list_by_xpath(Players.Profile.POSITION_OTHER),
        }
        self.response["foot"] = self.get_text_by_xpath(Players.Profile.FOOT)
        self.response["shirtNumber"] = self.get_text_by_xpath(Players.Profile.SHIRT_NUMBER)
        self.response["club"] = {
            "id": extract_from_url(self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_URL)),
            "name": self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_NAME),
            "joined": self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_JOINED),
            "contractExpires": self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_CONTRACT_EXPIRES),
            "contractOption": self.get_text_by_xpath(Players.Profile.CURRENT_CLUB_CONTRACT_OPTION),
            "lastClubID": extract_from_url(self.get_text_by_xpath(Players.Profile.LAST_CLUB_URL)),
            "lastClubName": self.get_text_by_xpath(Players.Profile.LAST_CLUB_NAME),
            "mostGamesFor": self.get_text_by_xpath(Players.Profile.MOST_GAMES_FOR_CLUB_NAME),
        }
        self.response["marketValue"] = self.get_text_by_xpath(Players.Profile.MARKET_VALUE, iloc_to=3, join_str="")
        self.response["agent"] = {
            "name": self.get_text_by_xpath(Players.Profile.AGENT_NAME),
            "url": self.get_text_by_xpath(Players.Profile.AGENT_URL),
        }
        self.response["outfitter"] = self.get_text_by_xpath(Players.Profile.OUTFITTER)
        self.response["socialMedia"] = self.get_list_by_xpath(Players.Profile.SOCIAL_MEDIA)
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
