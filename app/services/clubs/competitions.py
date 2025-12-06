from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubCompetitions(TransfermarktBase):
    """
    A class for retrieving and parsing the list of competitions a football club participates in from Transfermarkt.

    Args:
        club_id (str): The unique identifier of the football club.
        season_id (str): The unique identifier of the season.
        URL (str): The URL template for the club's game plan (spielplan) page on Transfermarkt.
    """

    club_id: str = None
    season_id: str = None
    URL: str = "https://www.transfermarkt.us/-/spielplan/verein/{club_id}/plus/0?saison_id={season_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktClubCompetitions class."""
        if self.season_id is None:
            # Default to current season
            self.season_id = str(datetime.now().year)
        self.URL = self.URL.format(club_id=self.club_id, season_id=self.season_id)
        self.page = self.request_url_page()
        # Check if Record table exists instead of heading
        record_table = self.page.xpath(Clubs.Competitions.RECORD_TABLE)
        if not record_table:
            raise HTTPException(status_code=404, detail=f"Invalid request (url: {self.URL})")

    def __parse_club_competitions(self) -> list[dict]:
        """
        Parse the club's game plan page and extract information about the competitions the club participates in.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains information about a competition,
                including the competition's unique identifier, name, and URL.
        """
        record_table = self.page.xpath(Clubs.Competitions.RECORD_TABLE)
        if not record_table:
            return []

        table = record_table[0]
        competition_rows = table.xpath(".//tr")

        competitions = []
        for row in competition_rows:
            # Find competition link in this row
            comp_link = row.xpath(Clubs.Competitions.COMPETITION_LINKS)
            if comp_link:
                href = comp_link[0].get("href", "")
                comp_id = extract_from_url(href)
                comp_name = "".join(comp_link[0].xpath(".//text()")).strip()

                if comp_id and comp_name:
                    competitions.append(
                        {
                            "id": comp_id,
                            "name": comp_name,
                            "url": href,
                        },
                    )

        return competitions

    def get_club_competitions(self) -> dict:
        """
        Retrieve and parse the list of competitions the specified football club participates in.

        Returns:
            dict: A dictionary containing the club's unique identifier, season identifier, list of competitions,
                  and the timestamp of when the data was last updated.
        """
        self.response["id"] = self.club_id
        self.response["seasonId"] = self.season_id
        self.response["competitions"] = self.__parse_club_competitions()

        return self.response
