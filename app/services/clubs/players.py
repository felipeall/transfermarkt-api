from dataclasses import dataclass
from typing import Optional

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_DOB
from app.utils.utils import extract_from_url, safe_regex, trim
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubPlayers(TransfermarktBase):
    """
    A class for retrieving and parsing the players of a football club from Transfermarkt.

    Args:
        club_id (str): The unique identifier of the football club.
        season_id (str): The unique identifier of the season.
        is_national_team (Optional[bool]): Explicit flag indicating if this is a national team.
                                          If None, will be detected automatically from DOM structure.
        URL (str): The URL template for the club's players page on Transfermarkt.
    """

    club_id: str = None
    season_id: str = None
    is_national_team: Optional[bool] = None
    URL: str = "https://www.transfermarkt.com/-/kader/verein/{club_id}/saison_id/{season_id}/plus/1"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktClubPlayers class."""
        # If season_id is None, use current year as default
        if self.season_id is None:
            from datetime import datetime

            self.season_id = str(datetime.now().year)
        self.URL = self.URL.format(club_id=self.club_id, season_id=self.season_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Clubs.Players.CLUB_NAME)
        self.__update_season_id()
        self.__update_past_flag()

    def __update_season_id(self):
        """Update the season ID if it's not provided by extracting it from the website."""
        # Only update if we can extract it from the page (for validation)
        try:
            extracted_season = extract_from_url(self.get_text_by_xpath(Clubs.Players.CLUB_URL), "season_id")
            if extracted_season and extracted_season != self.season_id:
                # Page shows different season, update it
                self.season_id = extracted_season
        except Exception:
            # If extraction fails, keep the original season_id
            pass

    def __update_past_flag(self) -> None:
        """Check if the season is the current or if it's a past one and update the flag accordingly."""
        self.past = "Current club" in self.get_list_by_xpath(Clubs.Players.PAST_FLAG)

    def __parse_club_players(self) -> list[dict]:
        """
        Parse player information from the webpage and return a list of dictionaries, each representing a player.

        Uses explicit is_national_team flag if provided, otherwise falls back to DOM-based heuristic detection.

        Returns:
            list[dict]: A list of player information dictionaries.
        """
        page_nationalities = self.page.xpath(Clubs.Players.PAGE_NATIONALITIES)
        page_players_infos = self.page.xpath(Clubs.Players.PAGE_INFOS)
        page_players_signed_from = self.page.xpath(
            Clubs.Players.Past.PAGE_SIGNED_FROM if self.past else Clubs.Players.Present.PAGE_SIGNED_FROM,
        )
        page_players_joined_on = self.page.xpath(
            Clubs.Players.Past.PAGE_JOINED_ON if self.past else Clubs.Players.Present.PAGE_JOINED_ON,
        )
        # Store the canonical URL list to ensure consistency across all derived lists
        players_urls = self.get_list_by_xpath(Clubs.Players.URLS)
        players_ids = [extract_from_url(url) for url in players_urls]
        players_names = self.get_list_by_xpath(Clubs.Players.NAMES)
        players_positions = self.get_list_by_xpath(Clubs.Players.POSITIONS)

        # Use explicit flag if provided, otherwise detect from DOM structure
        if self.is_national_team is not None:
            is_national_team = self.is_national_team
        else:
            # Fallback to DOM-based heuristic detection (no posrela structure)
            is_national_team = len(self.page.xpath(Clubs.Players.PAGE_INFOS)) == 0 and len(players_names) > 0

        # Handle national teams: extract data from rows directly
        if is_national_team:
            # Get all player rows (may contain duplicates for home/away)
            all_player_rows = self.page.xpath(
                "//div[@id='yw1']//tbody//tr[.//td[@class='hauptlink']//a[contains(@href, '/profil/spieler')]]",
            )

            # Extract data from rows, matching with player URLs in the same order as players_ids
            players_positions = []
            players_dobs_raw = []

            # Iterate over the same URL list used to create players_ids to maintain order and count
            for url in players_urls:
                # Find first row containing this player URL
                found = False
                for row in all_player_rows:
                    row_urls = row.xpath(".//td[@class='hauptlink']//a[contains(@href, '/profil/spieler')]/@href")
                    if url in row_urls:
                        tds = row.xpath(".//td")
                        # Position is in TD[4] for national teams
                        if len(tds) > 4:
                            pos_text = "".join(tds[4].xpath(".//text()")).strip()
                            players_positions.append(pos_text if pos_text else None)
                        else:
                            players_positions.append(None)

                        # DOB/Age is in TD[5] for national teams
                        if len(tds) > 5:
                            dob_text = "".join(tds[5].xpath(".//text()")).strip()
                            players_dobs_raw.append(dob_text if dob_text else None)
                        else:
                            players_dobs_raw.append(None)
                        found = True
                        break

                # URL not found in any row - append None to maintain alignment with players_ids
                if not found:
                    players_positions.append(None)
                    players_dobs_raw.append(None)

            players_dobs = [safe_regex(dob_age, REGEX_DOB, "dob") for dob_age in players_dobs_raw]
            players_ages = [safe_regex(dob_age, REGEX_DOB, "age") for dob_age in players_dobs_raw]
        else:
            # Regular club structure
            players_dobs = [
                safe_regex(dob_age, REGEX_DOB, "dob") for dob_age in self.get_list_by_xpath(Clubs.Players.DOB_AGE)
            ]
            players_ages = [
                safe_regex(dob_age, REGEX_DOB, "age") for dob_age in self.get_list_by_xpath(Clubs.Players.DOB_AGE)
            ]
        # Ensure all lists have the same length as players_ids
        base_length = len(players_ids)

        if len(players_names) != base_length:
            players_names = (players_names + [""] * base_length)[:base_length]
        players_nationalities = (
            [
                (
                    [trim(n) for n in nationality.xpath(Clubs.Players.NATIONALITIES) if trim(n)]
                    if nationality is not None
                    else []
                )
                for nationality in page_nationalities
            ]
            if page_nationalities
            else []
        )
        if len(players_nationalities) != base_length:
            players_nationalities = (players_nationalities + [[]] * base_length)[:base_length]

        players_current_club = (
            self.get_list_by_xpath(Clubs.Players.Past.CURRENT_CLUB) if self.past else [None] * base_length
        )
        if len(players_current_club) != base_length:
            players_current_club = (players_current_club + [None] * base_length)[:base_length]

        players_heights = self.get_list_by_xpath(
            Clubs.Players.Past.HEIGHTS if self.past else Clubs.Players.Present.HEIGHTS,
        )
        if len(players_heights) != base_length:
            players_heights = (players_heights + [None] * base_length)[:base_length]

        players_foots = self.get_list_by_xpath(
            Clubs.Players.Past.FOOTS if self.past else Clubs.Players.Present.FOOTS,
            remove_empty=False,
        )
        if len(players_foots) != base_length:
            players_foots = (players_foots + [None] * base_length)[:base_length]

        players_joined_on = (
            ["; ".join(e.xpath(Clubs.Players.JOINED_ON)) if e is not None else "" for e in page_players_joined_on]
            if page_players_joined_on
            else []
        )
        if len(players_joined_on) != base_length:
            players_joined_on = (players_joined_on + [""] * base_length)[:base_length]

        players_joined = (
            ["; ".join(e.xpath(Clubs.Players.JOINED)) if e is not None else "" for e in page_players_infos]
            if page_players_infos
            else []
        )
        if len(players_joined) != base_length:
            players_joined = (players_joined + [""] * base_length)[:base_length]

        players_signed_from = (
            ["; ".join(e.xpath(Clubs.Players.SIGNED_FROM)) if e is not None else "" for e in page_players_signed_from]
            if page_players_signed_from
            else []
        )
        if len(players_signed_from) != base_length:
            players_signed_from = (players_signed_from + [""] * base_length)[:base_length]

        players_contracts = (
            [None] * base_length if self.past else self.get_list_by_xpath(Clubs.Players.Present.CONTRACTS)
        )
        if len(players_contracts) != base_length:
            players_contracts = (players_contracts + [None] * base_length)[:base_length]

        players_marketvalues = self.get_list_by_xpath(Clubs.Players.MARKET_VALUES)
        if len(players_marketvalues) != base_length:
            players_marketvalues = (players_marketvalues + [None] * base_length)[:base_length]

        players_statuses = ["; ".join(e.xpath(Clubs.Players.STATUSES)) for e in page_players_infos if e is not None]
        if len(players_statuses) != base_length:
            players_statuses = (players_statuses + [None] * base_length)[:base_length]

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

    def get_club_players(self) -> dict:
        """
        Retrieve and parse player information for the specified football club.

        Returns:
            dict: A dictionary containing the club's unique identifier, player information, and the timestamp of when
                  the data was last updated.
        """
        self.response["id"] = self.club_id
        self.response["seasonId"] = self.season_id
        # Get club name from page
        club_name = self.get_text_by_xpath(Clubs.Players.CLUB_NAME)
        if club_name:
            self.response["name"] = club_name
        self.response["players"] = self.__parse_club_players()

        return self.response
