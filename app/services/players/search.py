from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree

from fastapi import HTTPException

from app.utils.utils import extract_from_url, get_list_by_xpath, request_url_page
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerSearch:
    query: str
    page_number: Optional[int] = 1

    def __post_init__(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}&Spieler_page={self.page_number}"
        self.page = request_url_page(url=search_url)
        self._check_player_found()

    def search_players(self) -> Optional[dict]:
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

        return {
            "query": self.query,
            "pageNumber": self.page_number,
            "lastPageNumber": self._get_last_page_number(),
            "results": [
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
                    "marketValue": market_value,
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
            ],
        }

    def _check_player_found(self) -> None:
        result_players: ElementTree = self.page.xpath(Players.Search.RESULT)
        if not result_players:
            raise HTTPException(status_code=404, detail=f"Player Search not found for name: {self.query}")
        else:
            self.page = result_players[0]

    def _get_last_page_number(self) -> int:
        url_page_number_last: list = self.page.xpath(Players.Search.PAGE_NUMBER_LAST)
        url_page_number_active: list = self.page.xpath(Players.Search.PAGE_NUMBER_ACTIVE)

        if url_page_number_last:
            last_page_number = int(url_page_number_last[0].split("=")[-1])
        else:
            last_page_number = int(url_page_number_active[0].split("=")[-1])

        return last_page_number
