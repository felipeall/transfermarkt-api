from dataclasses import dataclass, field

from fastapi import HTTPException

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    request_url_page,
)
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubPlayers:
    club_id: str
    season_id: str = None
    club_players: dict = field(default_factory=lambda: {})

    def get_club_players(self) -> dict:
        self._request_page()
        self._update_season_id()

        self.club_players["id"] = self.club_id
        self.club_players["clubName"] = get_text_by_xpath(self, Clubs.Players.CLUB_NAME)

        self._check_club_found()

        self.club_players["seasonYear"] = self.season_id
        self.club_players["players"] = self._parse_club_players()

        return clean_response(self.club_players)

    def _request_page(self) -> None:
        club_players_url = f"https://www.transfermarkt.com/-/kader/verein/{self.club_id}"
        if self.season_id:
            club_players_url += f"/saison_id/{self.season_id}"
        self.page = request_url_page(url=club_players_url)

    def _update_season_id(self):
        if not self.season_id:
            self.season_id = extract_from_url(get_text_by_xpath(self, Clubs.Players.CLUB_URL), "season_id")

    def _parse_club_players(self) -> list:
        page_nationalities = self.page.xpath(Clubs.Players.PAGE_NATIONALITIES)
        page_players_infos = self.page.xpath(Clubs.Players.PAGE_INFOS)

        players_names: list = get_list_by_xpath(self, Clubs.Players.NAMES)
        players_urls: list = get_list_by_xpath(self, Clubs.Players.URLS)
        players_positions: list = get_list_by_xpath(self, Clubs.Players.POSITIONS)
        players_ages: list = get_list_by_xpath(self, Clubs.Players.AGES)
        players_nationalities: list = [
            nationality.xpath(Clubs.Players.NATIONALITIES) for nationality in page_nationalities
        ]
        players_marketvalue: list = get_list_by_xpath(self, Clubs.Players.MARKET_VALUES)
        players_joined: list = ["; ".join(e.xpath(Clubs.Players.JOINED)) for e in page_players_infos]
        players_statuses: list = ["; ".join(e.xpath(Clubs.Players.STATUSES)) for e in page_players_infos]
        players_ids: list = [extract_from_url(url) for url in players_urls]

        return [
            {
                "id": idx,
                "name": name,
                "position": position,
                "age": age,
                "nationality": nationality,
                "marketValue": market_value,
                "joined": joined,
                "status": status,
            }
            for idx, name, position, age, nationality, market_value, joined, status in zip(
                players_ids,
                players_names,
                players_positions,
                players_ages,
                players_nationalities,
                players_marketvalue,
                players_joined,
                players_statuses,
            )
        ]

    def _check_club_found(self):
        if not self.club_players["clubName"]:
            raise HTTPException(status_code=404, detail=f"Club Players not found for id: {self.club_id}")
