from dataclasses import dataclass
from xml.etree import ElementTree

from app.utils.utils import request_url_page
from app.utils.xpath import Search


@dataclass
class TransfermarktSearch:
    query: str  # https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query=messi
    search_page: ElementTree = None

    def _request_search_page(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}"
        self.search_page = request_url_page(url=search_url)


class TransfermarktPlayerSearch(TransfermarktSearch):
    def search_player(self):
        self._request_search_page()

        result_players: ElementTree = self.search_page.xpath(Search.Players.RESULT_PLAYERS)[0]

        players_names: list = result_players.xpath(".//td[@class='hauptlink']//a//@title")
        players_urls: list = result_players.xpath(".//td[@class='hauptlink']//a//@href")
        players_ids: list = [url.split("/")[-1] for url in players_urls]
        players_codes: list = [url.split("/")[1] for url in players_urls]
        players_clubs: list = result_players.xpath(".//img[@class='tiny_wappen']//@title")

        return {
            id: {"code": code, "name": name, "current_club": club}
            for id, name, code, club in zip(players_ids, players_names, players_codes, players_clubs)
        }

        # return dict(zip(players_ids, players_names))

        # return {
        #     "players_names": players_names,
        #     "players_urls": players_urls,
        #     "players_ids": players_ids,
        # }
