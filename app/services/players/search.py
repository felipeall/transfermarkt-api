from dataclasses import dataclass
from xml.etree import ElementTree

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_CHART_CLUB_ID
from app.utils.utils import extract_from_url, safe_regex, trim
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerSearch(TransfermarktBase):
    """
    A class for searching football players on Transfermarkt and retrieving search results.

    Args:
        query (str): The search query for finding football clubs.
        URL (str): The URL template for the search query.
        page_number (int): The page number of search results (default is 1).
    """

    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Spieler_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self) -> None:
        """Initialize the TransfermarktPlayerSearch class."""
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Players.Search.FOUND)

    def __parse_search_results(self) -> list:
        """
        Parse and return a list of player search results. Each result includes player information such as their unique
        identifier, name, position, club (including ID and name), age, nationality, and market value.

        Returns:
            list: A list of dictionaries, with each dictionary representing a player search result.
        """
        # Get all result rows first
        search_results: list[ElementTree] = self.page.xpath(Players.Search.RESULTS)

        results = []
        for result in search_results:
            # Extract data from each row individually (relative XPath)
            id_list = result.xpath(Players.Search.ID)
            idx = extract_from_url(id_list[0] if id_list else None)

            name_list = result.xpath(Players.Search.NAME)
            name = trim(name_list[0]) if name_list and name_list[0] else None

            position_list = result.xpath(Players.Search.POSITION)
            position = trim(position_list[0]) if position_list and position_list[0] else None

            club_name_list = result.xpath(Players.Search.CLUB_NAME)
            club_name = trim(club_name_list[0]) if club_name_list and club_name_list[0] else None

            club_image_list = result.xpath(Players.Search.CLUB_IMAGE)
            club_id = safe_regex(club_image_list[0] if club_image_list else None, REGEX_CHART_CLUB_ID, "club_id")

            age_list = result.xpath(Players.Search.AGE)
            age = trim(age_list[0]) if age_list and age_list[0] else None

            # Nationalities - relative to this specific row (can be multiple)
            nationalities_list = result.xpath(Players.Search.NATIONALITIES)
            nationalities = [trim(n) for n in nationalities_list if n and trim(n)]

            market_value_list = result.xpath(Players.Search.MARKET_VALUE)
            market_value = trim(market_value_list[0]) if market_value_list and market_value_list[0] else None

            if idx:  # Only add if we have a valid ID
                results.append(
                    {
                        "id": idx,
                        "name": name,
                        "position": position,
                        "club": {
                            "name": club_name,
                            "id": club_id,
                        },
                        "age": age,
                        "nationalities": nationalities,
                        "marketValue": market_value,
                    },
                )

        return results

    def search_players(self) -> dict:
        """
        Retrieve and parse the search results for players matching the specified query. The results
            include player information such as their name, position, club, age, nationality, and market value.

        Returns:
            dict: A dictionary containing the search query, page number, last page number, search
                results, and the timestamp of when the data was last updated.
        """
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number(Players.Search.BASE)
        self.response["results"] = self.__parse_search_results()

        return self.response
