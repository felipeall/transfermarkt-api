from dataclasses import dataclass, field
from xml.etree import ElementTree

from transfermarkt_scrapper.utils.utils import clean_dict, request_player_page
from transfermarkt_scrapper.utils.xpath import Players


@dataclass
class TransfermarktPlayers:
    player_url: str

    player_info: dict = field(default_factory=lambda: {"type": "player"})
    player_page: ElementTree = None

    def get_player_info(self):
        self.player_page = request_player_page(url=self.player_url)

        # Profile
        self.player_info["id"] = self._get_text_by_xpath(Players.Profile.PLAYER_ID)
        self.player_info["url"] = self._get_text_by_xpath(Players.Profile.PLAYER_URL)

        # Header
        self.player_info["name"] = self._get_player_name()
        self.player_info["image_url"] = self._get_text_by_xpath(Players.Header.PLAYER_IMAGE_URL)
        self.player_info["shirt_number"] = self._get_text_by_xpath(Players.Header.SHIRT_NUMBER)
        self.player_info["current_club"] = {
            "id": self._get_text_by_xpath(Players.Profile.CURRENT_CLUB_ID),
            "url": self._get_text_by_xpath(Players.Header.CURRENT_CLUB_URL),
            "name": self._get_text_by_xpath(Players.Header.CURRENT_CLUB_NAME),
            "joined": self._get_text_by_xpath(Players.Header.CURRENT_CLUB_JOINED),
            "contract_expires": self._get_text_by_xpath(Players.Header.CURRENT_CLUB_CONTRACT_EXPIRES),
            "contract_option": self._get_text_by_xpath(Players.Header.CURRENT_CLUB_CONTRACT_OPTION),
        }

        # Data
        self.player_info["full_name"] = self._get_text_by_xpath(Players.Data.FULL_NAME)
        self.player_info["name_in_home_country"] = self._get_text_by_xpath(Players.Data.NAME_IN_HOME_COUNTRY)
        self.player_info["date_of_birth"] = self._get_text_by_xpath(Players.Data.DATE_OF_BIRTH)
        self.player_info["place_of_birth"] = {
            "city": self._get_text_by_xpath(Players.Data.PLACE_OF_BIRTH_CITY),
            "country": self._get_text_by_xpath(Players.Data.PLACE_OF_BIRTH_COUNTRY),
        }
        self.player_info["age"] = self._get_text_by_xpath(Players.Data.AGE)
        self.player_info["height"] = self._get_text_by_xpath(Players.Data.HEIGHT)
        self.player_info["citizenship"] = self._get_list_by_xpath(Players.Data.CITIZENSHIP)
        self.player_info["position"] = {
            "main": self._get_text_by_xpath(Players.Data.POSITION_MAIN),
            "other": self._get_list_by_xpath(Players.Data.POSITION_OTHER),
        }
        self.player_info["foot"] = self._get_text_by_xpath(Players.Data.FOOT)
        self.player_info["market_value"] = {
            "current": self._get_text_by_xpath(Players.Data.MARKET_VALUE_CURRENT),
            "highest": self._get_text_by_xpath(Players.Data.MARKET_VALUE_HIGHEST),
        }
        self.player_info["player_agent"] = {
            "name": self._get_text_by_xpath(Players.Data.PLAYER_AGENT_NAME),
            "url": self._get_text_by_xpath(Players.Data.PLAYER_AGENT_URL),
        }
        self.player_info["outfitter"] = self._get_text_by_xpath(Players.Data.OUTFITTER)
        self.player_info["social_media"] = self._get_list_by_xpath(Players.Data.SOCIAL_MEDIA)

        return clean_dict(self.player_info)

    def _get_player_name(self):
        player_header_data = self.player_page.xpath(Players.Header.PLAYER_NAME)
        player_header_data = [e.strip() for e in player_header_data if e.strip()]
        return " ".join(player_header_data[1:])

    def _get_text_by_xpath(self, xpath: str):
        try:
            element: str = self.player_page.xpath(xpath)[0].strip()
            return element.replace('\xa0', '')
        except IndexError:
            return None

    def _get_list_by_xpath(self, xpath: str) -> list:
        elements = self.player_page.xpath(xpath)
        elements = [e.strip() for e in elements if e.strip()]

        return elements
