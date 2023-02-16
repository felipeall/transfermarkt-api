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

        result_nationalities: ElementTree = result_players[0].xpath(Search.Players.RESULT_NATIONALITIES)

        players_names: list = result_players[0].xpath(Search.Players.PLAYERS_NAMES)
        players_urls: list = result_players[0].xpath(Search.Players.PLAYERS_URLS)
        players_clubs: list = result_players[0].xpath(Search.Players.PLAYERS_CLUB)
        players_market_values: list = result_players[0].xpath(Search.Players.PLAYERS_MARKET_VALUES)
        player_nationalities: list = [
            nationality.xpath(Search.Players.PLAYERS_NATIONALITIES) for nationality in result_nationalities
        ]
        players_ids: list = [url.split("/")[-1] for url in players_urls]
        players_codes: list = [url.split("/")[1] for url in players_urls]

        return [
            {
                "id": idx,
                "code": code,
                "name": name,
                "market_value": market_value,
                "nationality": nationality,
                "current_club": club,
                "url": url,
            }
            for idx, code, name, market_value, nationality, club, url in zip(
                players_ids,
                players_codes,
                players_names,
                players_market_values,
                player_nationalities,
                players_clubs,
                players_urls,
            )
        ]
