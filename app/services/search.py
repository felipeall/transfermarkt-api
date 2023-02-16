from dataclasses import dataclass
from xml.etree import ElementTree

from app.utils.utils import request_url_page
from app.utils.xpath import Search


@dataclass
class TransfermarktSearch:
    query: str
    search_page: ElementTree = None

    def _request_search_page(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}"
        self.search_page = request_url_page(url=search_url)


class TransfermarktPlayerSearch(TransfermarktSearch):
    def search_player(self):
        self._request_search_page()

        result_players: ElementTree = self.search_page.xpath(Search.Players.RESULT_PLAYERS)

        if not result_players:
            return None

        players_names: list = result_players[0].xpath(".//td[@class='hauptlink']//a//@title")
        players_urls: list = result_players[0].xpath(".//td[@class='hauptlink']//a//@href")
        players_clubs: list = result_players[0].xpath(".//img[@class='tiny_wappen']//@title")
        players_ids: list = [url.split("/")[-1] for url in players_urls]
        players_codes: list = [url.split("/")[1] for url in players_urls]

        return [
            {"id": idx, "code": code, "name": name, "url": url, "current_club": club}
            for idx, code, name, url, club in zip(
                players_ids, players_codes, players_names, players_urls, players_clubs
            )
        ]
