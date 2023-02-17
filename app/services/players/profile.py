from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from xml.etree import ElementTree

from app.utils.utils import clean_dict, extract_id_from_tfmkt_url, request_url_page
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerProfile:
    player_id: str
    player_info: dict = field(default_factory=lambda: {"type": "player"})

    def get_player_profile(self) -> dict:
        self._request_player_page()

        self.player_info["url"] = self._get_text_by_xpath(Players.Profile.URL)
        self.player_info["id"] = self._get_text_by_xpath(Players.Profile.ID)
        self.player_info["name"] = self._parse_player_name()
        self.player_info["full_name"] = self._get_text_by_xpath(Players.Profile.FULL_NAME)
        self.player_info["name_in_home_country"] = self._get_text_by_xpath(Players.Profile.NAME_IN_HOME_COUNTRY)
        self.player_info["image_url"] = self._get_text_by_xpath(Players.Profile.IMAGE_URL)
        self.player_info["date_of_birth"] = self._get_text_by_xpath(Players.Profile.DATE_OF_BIRTH)
        self.player_info["place_of_birth"] = {
            "city": self._get_text_by_xpath(Players.Profile.PLACE_OF_BIRTH_CITY),
            "country": self._get_text_by_xpath(Players.Profile.PLACE_OF_BIRTH_COUNTRY),
        }
        self.player_info["age"] = self._get_text_by_xpath(Players.Profile.AGE)
        self.player_info["height"] = self._get_text_by_xpath(Players.Profile.HEIGHT)
        self.player_info["citizenship"] = self._get_list_by_xpath(Players.Profile.CITIZENSHIP)
        self.player_info["position"] = {
            "main": self._get_text_by_xpath(Players.Profile.POSITION_MAIN),
            "other": self._get_list_by_xpath(Players.Profile.POSITION_OTHER),
        }
        self.player_info["foot"] = self._get_text_by_xpath(Players.Profile.FOOT)
        self.player_info["shirt_number"] = self._get_text_by_xpath(Players.Profile.SHIRT_NUMBER)
        self.player_info["current_club"] = {
            "club_id": extract_id_from_tfmkt_url(self._get_text_by_xpath(Players.Profile.CURRENT_CLUB_URL)),
            "club_name": self._get_text_by_xpath(Players.Profile.CURRENT_CLUB_NAME),
            "joined": self._get_text_by_xpath(Players.Profile.CURRENT_CLUB_JOINED),
            "contract_expires": self._get_text_by_xpath(Players.Profile.CURRENT_CLUB_CONTRACT_EXPIRES),
            "contract_option": self._get_text_by_xpath(Players.Profile.CURRENT_CLUB_CONTRACT_OPTION),
        }
        self.player_info["market_value"] = {
            "current": self._get_text_by_xpath(Players.Profile.MARKET_VALUE_CURRENT),
            "highest": self._get_text_by_xpath(Players.Profile.MARKET_VALUE_HIGHEST),
        }
        self.player_info["player_agent"] = {
            "name": self._get_text_by_xpath(Players.Profile.AGENT_NAME),
            "url": self._get_text_by_xpath(Players.Profile.AGENT_URL),
        }
        self.player_info["outfitter"] = self._get_text_by_xpath(Players.Profile.OUTFITTER)
        self.player_info["social_media"] = self._get_list_by_xpath(Players.Profile.SOCIAL_MEDIA)
        self.player_info["last_update"] = datetime.now()

        return clean_dict(self.player_info)

    def _request_player_page(self) -> None:
        player_url = f"https://www.transfermarkt.com/-/profil/spieler/{self.player_id}"
        self.player_page = request_url_page(url=player_url)

    def _parse_player_name(self) -> str:
        player_header_data: list = self.player_page.xpath(Players.Profile.NAME)
        player_header_data_valid: list = [e.strip() for e in player_header_data if e.strip()]
        player_name = " ".join(player_header_data_valid[1:])

        return player_name

    def _get_text_by_xpath(self, xpath: str) -> Optional[str]:
        element: ElementTree = self.player_page.xpath(xpath)

        if element:
            return self.player_page.xpath(xpath)[0].strip().replace("\xa0", "")
        else:
            return None

    def _get_list_by_xpath(self, xpath: str) -> Optional[list]:
        elements: list = self.player_page.xpath(xpath)
        elements_valid: list = [e.strip() for e in elements if e.strip()]

        return elements_valid or None
