from dataclasses import dataclass
from xml.etree import ElementTree

from fastapi import HTTPException

from app.services.commons.search import TransfermarktSearch
from app.utils.utils import clean_response, extract_from_url, get_list_by_xpath, trim
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionSearch(TransfermarktSearch):
    def search_competitions(self):
        self.result_competitions: ElementTree = self.page.xpath(Competitions.Search.RESULT)

        self._check_competition_found()

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

        return clean_response(
            [
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
            ]
        )

    def _check_competition_found(self) -> None:
        if not self.result_competitions:
            raise HTTPException(status_code=404, detail=f"Competition Search not found for name: {self.query}")
        else:
            self.page = self.result_competitions[0]
