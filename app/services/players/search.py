from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree

from app.services.commons.search import TransfermarktSearch
from app.utils.utils import extract_from_url, get_list_by_xpath
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerSearch(TransfermarktSearch):
    def search_players(self) -> Optional[list]:
        result_players: ElementTree = self.page.xpath(Players.Search.RESULT)

        if not result_players:
            return None
        else:
            self.page = result_players[0]

        result_nationalities: ElementTree = self.page.xpath(Players.Search.RESULT_NATIONALITIES)
        result_clubs: ElementTree = self.page.xpath(Players.Search.RESULT_CLUBS)

        players_urls: list = get_list_by_xpath(self, Players.Search.URLS)
        players_names: list = get_list_by_xpath(self, Players.Search.NAMES)
        players_clubs_names: list = get_list_by_xpath(self, Players.Search.CLUBS_NAMES)
        players_positions: list = get_list_by_xpath(self, Players.Search.POSITIONS)
        players_ages: list = get_list_by_xpath(self, Players.Search.AGES)
        players_market_values: list = get_list_by_xpath(self, Players.Search.MARKET_VALUES)
        player_nationalities: list = [
            nationality.xpath(Players.Search.NATIONALITIES) for nationality in result_nationalities
        ]
        players_ids: list = [extract_from_url(url) for url in players_urls]
        players_clubs_ids: list = [
            (
                extract_from_url(club.xpath(Players.Search.CLUBS_URLS)[0])
                if club.xpath(Players.Search.CLUBS_URLS)
                else "515"
            )
            for club in result_clubs
        ]

        return [
            {
                "id": idx,
                "url": url,
                "name": name,
                "club": {
                    "id": club_id,
                    "name": club_name,
                },
                "position": position,
                "age": age,
                "nationality": nationality,
                "market_value": market_value,
            }
            for idx, url, name, club_id, club_name, position, age, nationality, market_value in zip(
                players_ids,
                players_urls,
                players_names,
                players_clubs_ids,
                players_clubs_names,
                players_positions,
                players_ages,
                player_nationalities,
                players_market_values,
            )
        ]
