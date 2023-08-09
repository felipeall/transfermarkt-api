from dataclasses import dataclass, field

from fastapi import HTTPException

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    request_url_page,
    safe_regex,
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
        self._update_club_in_past()

        self.club_players["id"] = self.club_id
        self.club_players["clubName"] = get_text_by_xpath(self, Clubs.Players.CLUB_NAME)

        self._check_club_found()

        self.club_players["seasonYear"] = self.season_id
        self.club_players["players"] = self._parse_club_players()

        return clean_response(self.club_players)

    def _request_page(self) -> None:
        club_players_url = (
            f"https://www.transfermarkt.com/-/kader/verein/{self.club_id}/saison_id/{self.season_id}/plus/1"
        )
        self.page = request_url_page(url=club_players_url)

    def _update_season_id(self):
        if self.season_id is None:
            self.season_id = extract_from_url(get_text_by_xpath(self, Clubs.Players.CLUB_URL), "season_id")

    def _update_club_in_past(self):
        self.past = "Current club" in get_list_by_xpath(self, Clubs.Players.PAST_FLAG)

    def _parse_club_players(self) -> list:
        page_nationalities = self.page.xpath(Clubs.Players.PAGE_NATIONALITIES)
        page_players_infos = self.page.xpath(Clubs.Players.PAGE_INFOS)
        page_players_signed_from = self.page.xpath(
            Clubs.Players.Past.PAGE_SIGNED_FROM if self.past else Clubs.Players.Present.PAGE_SIGNED_FROM,
        )

        players_urls: list = get_list_by_xpath(self, Clubs.Players.URLS)
        players_ids: list = [extract_from_url(url) for url in players_urls]

        players_names: list = get_list_by_xpath(self, Clubs.Players.NAMES)

        players_positions: list = get_list_by_xpath(self, Clubs.Players.POSITIONS)
        players_dobs: list = [
            safe_regex(dob_age, r"^(?P<dob>.*)\s\((?P<age>\d*)\)", "dob")
            for dob_age in get_list_by_xpath(self, Clubs.Players.DOB_AGE)
        ]
        players_ages: list = [
            safe_regex(dob_age, r"^(?P<dob>.*)\s\((?P<age>\d*)\)", "age")
            for dob_age in get_list_by_xpath(self, Clubs.Players.DOB_AGE)
        ]
        players_nationalities: list = [
            nationality.xpath(Clubs.Players.NATIONALITIES) for nationality in page_nationalities
        ]
        players_current_club = (
            get_list_by_xpath(self, Clubs.Players.Past.CURRENT_CLUB) if self.past else [None] * len(players_ids)
        )
        players_heights: list = get_list_by_xpath(
            self,
            Clubs.Players.Past.HEIGHTS if self.past else Clubs.Players.Present.HEIGHTS,
        )
        players_foots: list = get_list_by_xpath(
            self,
            Clubs.Players.Past.FOOTS if self.past else Clubs.Players.Present.FOOTS,
            remove_empty=False,
        )
        players_joined_on: list = get_list_by_xpath(
            self,
            Clubs.Players.Past.JOINED_ON if self.past else Clubs.Players.Present.JOINED_ON,
        )
        players_joined: list = ["; ".join(e.xpath(Clubs.Players.JOINED)) for e in page_players_infos]
        players_signed_from: list = ["; ".join(e.xpath(Clubs.Players.SIGNED_FROM)) for e in page_players_signed_from]
        players_contracts: list = get_list_by_xpath(
            self,
            Clubs.Players.Past.CONTRACTS if self.past else Clubs.Players.Present.CONTRACTS,
        )
        players_marketvalues: list = get_list_by_xpath(self, Clubs.Players.MARKET_VALUES)
        players_statuses: list = ["; ".join(e.xpath(Clubs.Players.STATUSES)) for e in page_players_infos]

        return [
            {
                "id": idx,
                "name": name,
                "position": position,
                "dateOfBirth": dob,
                "age": age,
                "nationality": nationality,
                "currentClub": current_club,
                "height": height,
                "foot": foot,
                "joinedOn": joined_on,
                "joined": joined,
                "signedFrom": signed_from,
                "contract": contract,
                "marketValue": market_value,
                "status": status,
            }
            for idx, name, position, dob, age, nationality, current_club, height, foot, joined_on, joined, signed_from, contract, market_value, status, in zip(  # noqa: E501
                players_ids,
                players_names,
                players_positions,
                players_dobs,
                players_ages,
                players_nationalities,
                players_current_club,
                players_heights,
                players_foots,
                players_joined_on,
                players_joined,
                players_signed_from,
                players_contracts,
                players_marketvalues,
                players_statuses,
            )
        ]

    def _check_club_found(self) -> None:
        if not self.club_players["clubName"]:
            raise HTTPException(status_code=404, detail=f"Club Players not found for id: {self.club_id}")
