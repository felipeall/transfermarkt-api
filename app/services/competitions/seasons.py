from dataclasses import dataclass
from typing import Optional

from app.services.base import TransfermarktBase
from app.utils.utils import trim
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionSeasons(TransfermarktBase):
    """
    A class for retrieving and parsing the list of available seasons for a competition on Transfermarkt.

    Args:
        competition_id (str): The unique identifier of the competition.
        URL (str): The URL template for the competition's page on Transfermarkt.
    """

    competition_id: Optional[str] = None
    URL: str = "https://www.transfermarkt.com/-/startseite/wettbewerb/{competition_id}"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktCompetitionSeasons class."""
        self.URL = self.URL.format(competition_id=self.competition_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Competitions.Profile.NAME)

    def __detect_competition_type(self, season_name: str) -> bool:
        """
        Detect if competition is cross-year (e.g., "25/26") or single-year (e.g., "2025").

        Args:
            season_name (str): The season name from the dropdown.

        Returns:
            bool: True if cross-year (contains "/"), False if single-year.
        """
        return "/" in season_name

    def __parse_season_to_years(self, season_name: str) -> tuple[int, int]:
        """
        Parse season name to start_year and end_year.

        Args:
            season_name (str): The season name (e.g., "25/26" or "2025").

        Returns:
            tuple[int, int]: A tuple containing (start_year, end_year).
        """
        season_name = trim(season_name)
        is_cross_year = self.__detect_competition_type(season_name)

        if is_cross_year:
            # Cross-year format: "25/26" -> start_year: 2025, end_year: 2026
            # Handle both "25/26" and "2024/25" formats, and old seasons like "99/00"
            parts = season_name.split("/")
            if len(parts) == 2:
                start_part = parts[0].strip()
                end_part = parts[1].strip()

                # Parse start year
                if len(start_part) == 2:
                    start_num = int(start_part)
                    # If start is >= 90, it's likely 1900s (e.g., "99/00" = 1999/2000)
                    # Otherwise assume 2000s (e.g., "25/26" = 2025/2026)
                    if start_num >= 90:
                        start_year = 1900 + start_num
                    else:
                        start_year = 2000 + start_num
                else:
                    start_year = int(start_part)

                # Parse end year
                if len(end_part) == 2:
                    end_num = int(end_part)
                    start_num = int(start_part) if len(start_part) == 2 else (start_year % 100)
                    # If end is less than start (e.g., "99/00"), it means we crossed century
                    # So if start is 1999, end should be 2000
                    if end_num < start_num:
                        # Crossed century boundary - end is in next century
                        if start_year >= 2000:
                            end_year = 2000 + end_num
                        else:
                            # Start is in 1900s, end is in 2000s
                            end_year = 2000 + end_num
                    else:
                        # Same century as start
                        if start_year >= 2000:
                            end_year = 2000 + end_num
                        else:
                            end_year = 1900 + end_num
                else:
                    end_year = int(end_part)

                return (start_year, end_year)
        else:
            # Single-year format: "2025" -> start_year: 2025, end_year: 2025
            try:
                year = int(season_name)
                return (year, year)
            except ValueError:
                # Handle malformed input (non-numeric season_name)
                return (None, None)

        # Fallback: return None values if parsing fails
        return (None, None)

    def __parse_season_id_from_name(self, season_name: str) -> str:
        """
        Extract season_id from season name.
        For cross-year: "25/26" -> "2025", "99/00" -> "1999"
        For single-year: "2025" -> "2025"

        Args:
            season_name (str): The season name from the dropdown.

        Returns:
            str: The season_id (start year as string).
        """
        season_name = trim(season_name)
        is_cross_year = self.__detect_competition_type(season_name)

        if is_cross_year:
            # Cross-year: extract start year
            parts = season_name.split("/")
            if len(parts) == 2:
                start_part = parts[0].strip()
                if len(start_part) == 2:
                    start_num = int(start_part)
                    # If start is >= 90, it's likely 1900s (e.g., "99/00" = 1999)
                    # Otherwise assume 2000s (e.g., "25/26" = 2025)
                    if start_num >= 90:
                        return str(1900 + start_num)
                    else:
                        return str(2000 + start_num)
                else:
                    return start_part
        else:
            # Single-year: return as is
            return season_name

        return season_name

    def __parse_seasons(self) -> list[dict]:
        """
        Parse the competition's page and extract all available seasons from the dropdown.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains information about a season,
                including season_id, season_name, start_year, and end_year.
        """
        # First, try to get seasons directly from the table cell text
        # The HTML shows seasons as plain text in a td: "25/26 24/25 23/24 ..."
        season_text_raw = self.page.xpath(Competitions.Profile.SEASON_TABLE_CELL)

        if season_text_raw:
            # Join all text nodes and split by whitespace to get individual seasons
            combined_text = " ".join([trim(s) for s in season_text_raw if trim(s)])
            # Remove "Show" button text if present
            combined_text = combined_text.replace("Show", "").strip()
            # Split by whitespace - seasons are space-separated
            season_options = [s.strip() for s in combined_text.split() if s.strip()]
        else:
            # Fallback: Find the season dropdown container - try multiple XPath patterns
            season_dropdown = self.page.xpath(Competitions.Profile.SEASON_DROPDOWN)

            # If not found, try alternative patterns
            if not season_dropdown:
                # Try finding table with season filter
                season_dropdown = self.page.xpath(
                    "//table//td[contains(text(), 'Filter by season:')]/following-sibling::td[1]",
                )

            if not season_dropdown:
                # Try finding any table row containing "Filter by season"
                season_dropdown = self.page.xpath("//tr[contains(., 'Filter by season:')]//td[2]")

            # If dropdown container found, use it
            if season_dropdown:
                dropdown = season_dropdown[0]

                # Get all season options from the dropdown list - try multiple patterns
                season_options = dropdown.xpath(Competitions.Profile.SEASON_OPTIONS)

                # If no options found, try alternative XPath patterns
                if not season_options:
                    # Try to get from selected link if dropdown is not expanded
                    selected_season = dropdown.xpath(Competitions.Profile.SEASON_SELECTED)
                    if selected_season:
                        season_options = [trim(selected_season[0])]

                # Also try to get from list items directly (more generic pattern)
                if not season_options:
                    # Try multiple list item patterns
                    season_options = dropdown.xpath(
                        ".//li//text() | " ".//listitem//text() | " ".//ul//li//text() | " ".//list//listitem//text()",
                    )
                    season_options = [trim(s) for s in season_options if trim(s)]

                # Try even more generic pattern - get all text nodes in dropdown
                if not season_options:
                    all_text = dropdown.xpath(".//text()")
                    combined_text = " ".join([trim(s) for s in all_text if trim(s)])
                    # Split by whitespace to get individual seasons
                    season_options = [
                        s.strip() for s in combined_text.split() if s.strip() and ("/" in s or s.strip().isdigit())
                    ]
            else:
                # Fallback: try to find seasons directly from the page
                # Look for list items in tables that might contain season info
                season_options = self.page.xpath(
                    "//table[contains(., 'Filter by season:')]//li//text() | "
                    "//table//td[contains(., 'Filter by season:')]/following-sibling::td//li//text() | "
                    "//table//td[contains(., 'Filter by season:')]/following-sibling::td//listitem//text() | "
                    "//table//tr[contains(., 'Filter by season:')]//li//text()",
                )
                season_options = [trim(s) for s in season_options if trim(s)]

        # Clean up season_options - remove empty strings
        season_options = [trim(s) for s in season_options if trim(s)]

        # If we got a single string with multiple seasons (space-separated), split it
        # This handles the case where seasons are in plain text like "25/26 24/25 23/24 ..."
        if len(season_options) == 1 and " " in season_options[0]:
            combined = season_options[0]
            # Split by whitespace to get individual seasons
            season_options = [s.strip() for s in combined.split() if s.strip()]
        elif len(season_options) > 0:
            # Check if first item contains multiple seasons
            first_item = season_options[0]
            if " " in first_item and ("/" in first_item or any(c.isdigit() for c in first_item)):
                # Split the first item if it contains multiple seasons
                split_seasons = [s.strip() for s in first_item.split() if s.strip()]
                # Replace first item with split seasons and keep rest
                season_options = split_seasons + season_options[1:]

        seasons = []
        seen_seasons = set()

        for season_text in season_options:
            season_name = trim(season_text)
            if not season_name or season_name in seen_seasons:
                continue

            seen_seasons.add(season_name)

            # Skip non-season entries like "Show" button text
            skip_words = ["show", "filter", "by", "season:", "filter by season:"]
            if season_name.lower() in skip_words:
                continue

            # Only process items that look like seasons (contain "/" or are 4-digit years)
            is_season = "/" in season_name or (  # Cross-year format like "25/26"
                season_name.isdigit() and len(season_name) == 4
            )  # Single year like "2025"

            if not is_season:
                continue

            # Parse season to years
            start_year, end_year = self.__parse_season_to_years(season_name)

            if start_year is not None and end_year is not None:
                season_id = self.__parse_season_id_from_name(season_name)
                seasons.append(
                    {
                        "seasonId": season_id,
                        "seasonName": season_name,
                        "startYear": start_year,
                        "endYear": end_year,
                    },
                )

        # Sort seasons by startYear descending (newest first)
        seasons.sort(key=lambda x: x["startYear"], reverse=True)

        return seasons

    def get_competition_seasons(self) -> dict:
        """
        Retrieve and parse all available seasons for a specific competition.

        Returns:
            dict: A dictionary containing the competition's unique identifier, name, list of seasons
                  with their start_year and end_year, and the timestamp of when the data was last updated.
        """
        self.response["id"] = self.competition_id
        self.response["name"] = self.get_text_by_xpath(Competitions.Profile.NAME)
        self.response["seasons"] = self.__parse_seasons()

        return self.response
