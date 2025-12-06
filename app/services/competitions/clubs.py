import logging
from dataclasses import dataclass
from typing import Optional

from app.services.base import TransfermarktBase
from app.settings import settings
from app.utils.utils import extract_from_url, trim
from app.utils.xpath import Competitions

logger = logging.getLogger(__name__)

# Mapping of national team competition IDs to their URL slugs
NATIONAL_TEAM_COMPETITIONS = {
    "FIWC": "world-cup",
    "EURO": "uefa-euro",
    "COPA": "copa-america",
    "AFAC": "afc-asian-cup",
    "GOCU": "gold-cup",
    "AFCN": "africa-cup",
}


@dataclass
class TransfermarktCompetitionClubs(TransfermarktBase):
    """
    A class for retrieving and parsing the list of football clubs in a specific competition on Transfermarkt.

    Args:
        competition_id (str): The unique identifier of the competition.
        season_id (str): The season identifier. If not provided, it will be extracted from the URL.
        URL (str): The URL template for the competition's page on Transfermarkt.
    """

    competition_id: Optional[str] = None
    season_id: Optional[str] = None
    URL: str = "https://www.transfermarkt.com/-/startseite/wettbewerb/{competition_id}/plus/?saison_id={season_id}"
    is_national_team: bool = False

    def __is_national_team_competition(self) -> bool:
        """
        Check if the competition is a national team competition.

        Returns:
            bool: True if the competition is a national team competition, False otherwise.
        """
        return self.competition_id in NATIONAL_TEAM_COMPETITIONS

    def __get_national_team_url(self) -> str:
        """
        Construct the URL for national team competition participants page.

        Returns:
            str: The URL for the participants page.
        """
        slug = NATIONAL_TEAM_COMPETITIONS.get(self.competition_id)
        if not slug:
            raise ValueError(f"Unknown national team competition: {self.competition_id}")

        # For national teams, season_id in URL is the year BEFORE the tournament
        # E.g., 2006 World Cup uses saison_id=2005
        url_season_id = self.season_id
        if url_season_id and url_season_id.isdigit():
            try:
                year = int(url_season_id)
                url_season_id = str(year - 1)
            except ValueError:
                pass

        return (
            f"https://www.transfermarkt.com/{slug}/teilnehmer/"
            f"pokalwettbewerb/{self.competition_id}/saison_id/{url_season_id}"
        )

    def __post_init__(self) -> None:
        """Initialize the TransfermarktCompetitionClubs class."""
        self.is_national_team = self.__is_national_team_competition()

        if self.is_national_team:
            # Use participants URL for national team competitions
            self.URL = self.__get_national_team_url()
        else:
            # Use normal URL for regular leagues
            self.URL = self.URL.format(
                competition_id=self.competition_id,
                season_id=self.season_id,
            )

        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Competitions.Profile.NAME)

    def __parse_competition_clubs(self) -> list:
        """
        Parse the competition's page and extract information about the football clubs participating
            in the competition.

        Returns:
            list: A list of dictionaries, where each dictionary contains information about a
                football club in the competition, including the club's unique identifier and name.
        """
        if self.is_national_team:
            # Use participants table XPath for national team competitions
            urls = self.get_list_by_xpath(Competitions.Clubs.PARTICIPANTS_URLS)
            names = self.get_list_by_xpath(Competitions.Clubs.PARTICIPANTS_NAMES)

            # Some tournament pages may include extra teams from "not qualified" section
            # Limit based on expected tournament size from configuration to avoid including non-participants
            # Tournament sizes can be configured via environment variables (e.g., TOURNAMENT_SIZE_FIWC=48)
            # See app/settings.py for available configuration options
            expected_size = settings.get_tournament_size(self.competition_id)

            if expected_size and len(urls) > expected_size:
                # Limit to expected size to exclude any extra teams from "not qualified" section
                urls = urls[:expected_size]
                names = names[:expected_size]
            elif expected_size is None:
                # Log warning if tournament size is not configured
                logger.warning(
                    f"Expected tournament size not configured for competition {self.competition_id}. "
                    f"Found {len(urls)} participants. "
                    f"To configure, set TOURNAMENT_SIZE_{self.competition_id} environment variable. "
                    f"Proceeding without truncation - all participants will be included.",
                )
        else:
            # Use normal XPath for regular leagues
            urls = self.get_list_by_xpath(Competitions.Clubs.URLS)
            names = self.get_list_by_xpath(Competitions.Clubs.NAMES)

        ids = [extract_from_url(url) for url in urls]

        # Validate that ids and names have the same length to prevent silent data loss
        if len(ids) != len(names):
            error_msg = (
                f"Data mismatch: found {len(ids)} IDs but {len(names)} names "
                f"for competition {self.competition_id} (URL: {self.URL}). "
                f"This indicates a parsing error that could cause data loss or misalignment."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        return [{"id": idx, "name": name} for idx, name in zip(ids, names)]

    def __get_competition_name(self) -> str:
        """
        Get the competition name, handling both regular leagues and national team competitions.

        Returns:
            str: The competition name.
        """
        name = self.get_text_by_xpath(Competitions.Profile.NAME)

        # Clean up name for national team competitions
        if self.is_national_team and name:
            name = trim(name)
            # Remove common prefixes/suffixes from participants pages
            name = name.replace("Participating teams in the ", "")
            name = name.replace(" - Participants", "")
            # Split by " - " and take first part if it contains year
            if " - " in name:
                parts = [p.strip() for p in name.split(" - ")]
                # Take the part that doesn't contain "Participants" or is the longest
                name = next((p for p in parts if "Participants" not in p and len(p) > 3), parts[0])
            # Remove any remaining "Participants" text
            name = name.replace("Participants", "").strip()

        return name

    def get_competition_clubs(self) -> dict:
        """
        Retrieve and parse the list of football clubs participating in a specific competition.

        Returns:
            dict: A dictionary containing the competition's unique identifier, name, season identifier, list of clubs
                  participating in the competition, and the timestamp of when the data was last updated.
        """
        self.response["id"] = self.competition_id
        self.response["name"] = self.__get_competition_name()

        if self.is_national_team:
            # For national teams, extract season_id from URL and convert back to tournament year
            # URL has saison_id=2005 for 2006 World Cup, so we add 1
            url_season_id = extract_from_url(
                self.get_text_by_xpath(Competitions.Profile.URL),
                "season_id",
            )
            if url_season_id and url_season_id.isdigit():
                # Convert back to tournament year (add 1)
                # isdigit() check prevents ValueError, so no try/except needed
                self.response["seasonId"] = str(int(url_season_id) + 1)
            elif url_season_id:
                # Use extracted season_id if it exists but is not a digit
                self.response["seasonId"] = url_season_id
            elif self.season_id:
                # Use provided season_id if URL extraction fails
                self.response["seasonId"] = self.season_id
        else:
            # For regular leagues, extract season_id normally
            season_id = extract_from_url(
                self.get_text_by_xpath(Competitions.Profile.URL),
                "season_id",
            )
            # Only include seasonId if it was found
            if season_id:
                self.response["seasonId"] = season_id

        self.response["clubs"] = self.__parse_competition_clubs()

        return self.response
