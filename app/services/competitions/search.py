from dataclasses import dataclass
from typing import Optional
from xml.etree import ElementTree

from fastapi import HTTPException

from app.utils.utils import extract_from_url, get_list_by_xpath, request_url_page, trim
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionSearch:
    query: str
    page_number: Optional[int] = 1

    def __post_init__(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}&Wettbewerb_page={self.page_number}"
        self.page = request_url_page(url=search_url)
        self._check_competition_found()

    def search_competitions(self):
        result_countries: ElementTree = self.page.xpath(Competitions.Search.RESULT_COUNTRIES)
        result_clubs: ElementTree = self.page.xpath(Competitions.Search.RESULT_CLUBS)
        result_players: ElementTree = self.page.xpath(Competitions.Search.RESULT_PLAYERS)
        result_marketvalues: ElementTree = self.page.xpath(Competitions.Search.RESULT_MARKETVALUES)
        result_continents: ElementTree = self.page.xpath(Competitions.Search.RESULT_CONTINENTS)

        names: list = get_list_by_xpath(self, Competitions.Search.NAMES)
        urls: list = get_list_by_xpath(self, Competitions.Search.URLS)

        countries: list = [trim(e.xpath(Competitions.Search.COUNTRIES)) for e in result_countries]
        clubs: list = [trim(e.xpath(Competitions.Search.CLUBS)) for e in result_clubs]
        players: list = [trim(e.xpath(Competitions.Search.PLAYERS)) for e in result_players]
        marketvalues: list = [trim(e.xpath(Competitions.Search.MARKETVALUES)) for e in result_marketvalues]
        continents: list = [trim(e.xpath(Competitions.Search.CONTINENTS)) for e in result_continents]

        ids: list = [extract_from_url(url) for url in urls]

        return {
            "query": self.query,
            "pageNumber": self.page_number,
            "lastPageNumber": self._get_last_page_number(),
            "results": [
                {
                    "id": idx,
                    "name": name,
                    "country": country,
                    "continent": continent,
                    "clubs": clubs,
                    "players": players,
                    "marketValue": marketvalue,
                }
                for idx, name, country, continent, clubs, players, marketvalue, in zip(
                    ids,
                    names,
                    countries,
                    continents,
                    clubs,
                    players,
                    marketvalues,
                )
            ],
        }

    def _check_competition_found(self) -> None:
        result_competitions: ElementTree = self.page.xpath(Competitions.Search.RESULT)
        if not result_competitions:
            raise HTTPException(status_code=404, detail=f"Competition Search not found for name: {self.query}")
        else:
            self.page = result_competitions[0]

    def _get_last_page_number(self) -> int:
        url_page_number_last: list = self.page.xpath(Competitions.Search.PAGE_NUMBER_LAST)
        url_page_number_active: list = self.page.xpath(Competitions.Search.PAGE_NUMBER_ACTIVE)

        if url_page_number_last:
            return int(url_page_number_last[0].split("=")[-1])
        elif url_page_number_active:
            return int(url_page_number_active[0].split("=")[-1])
        else:
            return 1
