import json
from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_CHART_CLUB_ID
from app.utils.utils import (
    clean_response,
    safe_regex,
    zip_lists_into_dict,
)
from app.utils.xpath import Players


from dataclasses import dataclass
from typing import Optional, List
from xml.etree import ElementTree
from lxml import etree
from fastapi import APIRouter, HTTPException

@dataclass
class TransfermarktPlayerInjuries(TransfermarktBase):

    player_id: str = None
    URL: str = "https://www.transfermarkt.com/player/verletzungen/spieler/{player_id}"

    def __post_init__(self):
        # injuries_url = f"https://www.transfermarkt.com/player/verletzungen/spieler/{self.player_id}"
        self.URL = self.URL.format(player_id=self.player_id)
        self.page = self.request_url_page()
        self._check_injuries_found()

    def get_player_injuries(self) -> Optional[List[dict]]:
        injuries_elements: ElementTree = self.page.xpath(Players.Injuries.RESULTS)
        injuries = []

        for injury_element in injuries_elements:
            season = injury_element.xpath(Players.Injuries.SEASONS)[0].text
            type_ = injury_element.xpath(Players.Injuries.INJURY)[0].text
            from_ = injury_element.xpath(Players.Injuries.FROM)[0].text
            to_ = injury_element.xpath(Players.Injuries.UNTIL)[0].text
            days = injury_element.xpath(Players.Injuries.DAYS)[0].text
            games_missed_list = injury_element.xpath(Players.Injuries.GAMES_MISSED)
            games_missed = games_missed_list[0].text.strip() if games_missed_list else '0'  # Handle missing span

            injuries.append({
                "season": season,
                "type": type_,
                "from": from_,
                "to": to_,
                "days": days,
                "games_missed": games_missed
            })

        return injuries

    def _check_injuries_found(self) -> None:
        result_injuries: ElementTree = self.page.xpath(Players.Injuries.RESULTS)
        if not result_injuries:
            raise HTTPException(status_code=404, detail=f"Injury data not found for player ID: {self.player_id}")

        # Debug print
        for inj in result_injuries:
            print(etree.tostring(inj, pretty_print=True).decode('utf-8'))




