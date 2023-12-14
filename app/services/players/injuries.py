from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from xml.etree import ElementTree

from app.services.base import TransfermarktBase
from app.utils.utils import clean_response, extract_from_url, trim
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerInjuries(TransfermarktBase):
    player_id: str = None
    URL: str = "https://www.transfermarkt.com/player/verletzungen/spieler/{player_id}/plus/1/page/{page_number}"
    page_number: int = 1

    def __post_init__(self):
        self.URL = self.URL.format(player_id=self.player_id, page_number=self.page_number)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Profile.URL)

    def __parse_player_injuries(self) -> Optional[List[dict]]:
        injuries: ElementTree = self.page.xpath(Players.Injuries.RESULTS)
        player_injuries = []

        for injury in injuries:
            season = trim(injury.xpath(Players.Injuries.SEASONS))
            injury_type = trim(injury.xpath(Players.Injuries.INJURY))
            date_from = trim(injury.xpath(Players.Injuries.FROM))
            date_until = trim(injury.xpath(Players.Injuries.UNTIL))
            days = trim(injury.xpath(Players.Injuries.DAYS))
            games_missed = trim(injury.xpath(Players.Injuries.GAMES_MISSED))
            games_missed_clubs_urls = injury.xpath(Players.Injuries.GAMES_MISSED_CLUBS_URLS)
            games_missed_clubs_ids = [extract_from_url(club_url) for club_url in games_missed_clubs_urls]

            player_injuries.append(
                {
                    "season": season,
                    "injury": injury_type,
                    "from": date_from,
                    "until": date_until,
                    "days": days,
                    "gamesMissed": games_missed,
                    "gamesMissedClubs": games_missed_clubs_ids,
                },
            )

        return player_injuries

    def get_player_injuries(self) -> dict:
        self.response["id"] = self.player_id
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number()
        self.response["injuries"] = self.__parse_player_injuries()
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
