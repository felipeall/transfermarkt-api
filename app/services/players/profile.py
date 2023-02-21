from dataclasses import dataclass, field
from datetime import datetime

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    request_url_page,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerProfile:
    player_id: str
    player_info: dict = field(default_factory=lambda: {"type": "player"})

    def get_player_profile(self) -> dict:
        self._request_player_page()

        self.player_info["url"] = get_text_by_xpath(self, Players.Profile.URL)
        self.player_info["id"] = get_text_by_xpath(self, Players.Profile.ID)
        self.player_info["name"] = self._parse_player_name()
        self.player_info["full_name"] = get_text_by_xpath(self, Players.Profile.FULL_NAME)
        self.player_info["name_in_home_country"] = get_text_by_xpath(self, Players.Profile.NAME_IN_HOME_COUNTRY)
        self.player_info["image_url"] = get_text_by_xpath(self, Players.Profile.IMAGE_URL)
        self.player_info["date_of_birth"] = get_text_by_xpath(self, Players.Profile.DATE_OF_BIRTH)
        self.player_info["place_of_birth"] = {
            "city": get_text_by_xpath(self, Players.Profile.PLACE_OF_BIRTH_CITY),
            "country": get_text_by_xpath(self, Players.Profile.PLACE_OF_BIRTH_COUNTRY),
        }
        self.player_info["age"] = get_text_by_xpath(self, Players.Profile.AGE)
        self.player_info["height"] = get_text_by_xpath(self, Players.Profile.HEIGHT)
        self.player_info["citizenship"] = get_list_by_xpath(self, Players.Profile.CITIZENSHIP)
        self.player_info["position"] = {
            "main": get_text_by_xpath(self, Players.Profile.POSITION_MAIN),
            "other": get_list_by_xpath(self, Players.Profile.POSITION_OTHER),
        }
        self.player_info["foot"] = get_text_by_xpath(self, Players.Profile.FOOT)
        self.player_info["shirt_number"] = get_text_by_xpath(self, Players.Profile.SHIRT_NUMBER)
        self.player_info["current_club"] = {
            "club_id": extract_from_url(get_text_by_xpath(self, Players.Profile.CURRENT_CLUB_URL)),
            "club_name": get_text_by_xpath(self, Players.Profile.CURRENT_CLUB_NAME),
            "joined": get_text_by_xpath(self, Players.Profile.CURRENT_CLUB_JOINED),
            "contract_expires": get_text_by_xpath(self, Players.Profile.CURRENT_CLUB_CONTRACT_EXPIRES),
            "contract_option": get_text_by_xpath(self, Players.Profile.CURRENT_CLUB_CONTRACT_OPTION),
        }
        self.player_info["market_value"] = {
            "current": get_text_by_xpath(self, Players.Profile.MARKET_VALUE_CURRENT),
            "highest": get_text_by_xpath(self, Players.Profile.MARKET_VALUE_HIGHEST),
        }
        self.player_info["player_agent"] = {
            "name": get_text_by_xpath(self, Players.Profile.AGENT_NAME),
            "url": get_text_by_xpath(self, Players.Profile.AGENT_URL),
        }
        self.player_info["outfitter"] = get_text_by_xpath(self, Players.Profile.OUTFITTER)
        self.player_info["social_media"] = get_list_by_xpath(self, Players.Profile.SOCIAL_MEDIA)
        self.player_info["last_update"] = datetime.now()

        return clean_response(self.player_info)

    def _request_player_page(self) -> None:
        player_url = f"https://www.transfermarkt.com/-/profil/spieler/{self.player_id}"
        self.page = request_url_page(url=player_url)

    def _parse_player_name(self) -> str:
        player_header_data: list = get_list_by_xpath(self, Players.Profile.NAME)
        player_name = " ".join(player_header_data[1:])

        return player_name
