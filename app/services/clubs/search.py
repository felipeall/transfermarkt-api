from dataclasses import dataclass

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubSearch(TransfermarktBase):
    """
    A class for searching football clubs on Transfermarkt and retrieving search results.

    Args:
        query (str): The search query for finding football clubs.
        URL (str): The URL template for the search query.
        page_number (int): The page number of search results (default is 1).
    """

    query: str = None
    URL: str = (
        "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={query}&Verein_page={page_number}"
    )
    page_number: int = 1

    def __post_init__(self) -> None:
        """Initialize the TransfermarktClubSearch class."""
        self.URL = self.URL.format(query=self.query, page_number=self.page_number)
        try:
            self.page = self.request_url_page()
            # Validate page was successfully loaded
            if self.page is None:
                raise ValueError(f"Failed to load page for URL: {self.URL}")
        except Exception as e:
            print(f"Failed to initialize TransfermarktClubSearch for {self.URL}: {e}")
            raise

    def __parse_search_results(self) -> list:
        """
        Parse the search results page and extract information about the found football clubs.

        Returns:
            list: A list of dictionaries, where each dictionary contains information about a
                football club found in the search results, including the club's unique identifier,
                URL, name, country, squad size, and market value.
        """
        # Debug: Check if page is valid
        if self.page is None:
            print(f"ERROR: Page is None for {self.URL}")
            return []

        # Debug: Try to get a sample of page content
        try:
            from lxml import etree

            page_html = etree.tostring(self.page, encoding="unicode")
            if page_html and len(page_html) > 0:
                print(f"Page HTML length: {len(page_html)}")
                # Check if page contains expected content
                if "transfermarkt" not in page_html.lower():
                    print("WARNING: Page doesn't contain 'transfermarkt' - might be blocked or wrong page")
        except Exception as e:
            print(f"ERROR: Could not serialize page: {e}")

        clubs_names = self.get_list_by_xpath(Clubs.Search.NAMES)
        clubs_urls = self.get_list_by_xpath(Clubs.Search.URLS)
        clubs_countries = self.get_list_by_xpath(Clubs.Search.COUNTRIES)
        clubs_squads = self.get_list_by_xpath(Clubs.Search.SQUADS)
        clubs_market_values = self.get_list_by_xpath(Clubs.Search.MARKET_VALUES)

        # Debug: Log what we found
        print(f"DEBUG: Found {len(clubs_names)} names, {len(clubs_urls)} URLs, {len(clubs_countries)} countries")
        if len(clubs_names) == 0:
            print("WARNING: No clubs found! XPath might be wrong or page structure changed")
            print(f"XPath NAMES: {Clubs.Search.NAMES}")
        clubs_ids = [extract_from_url(url) for url in clubs_urls]

        return [
            {
                "id": idx,
                "url": url,
                "name": name,
                "country": country,
                "squad": squad,
                "marketValue": market_value,
            }
            for idx, url, name, country, squad, market_value in zip(
                clubs_ids,
                clubs_urls,
                clubs_names,
                clubs_countries,
                clubs_squads,
                clubs_market_values,
            )
        ]

    def search_clubs(self) -> dict:
        """
        Perform a search for football clubs on Transfermarkt and retrieve search results.

        Returns:
            dict: A dictionary containing the search query, current page number, last page number,
                search results, and the timestamp of when the search was conducted.
        """
        self.response["query"] = self.query
        self.response["pageNumber"] = self.page_number
        self.response["lastPageNumber"] = self.get_last_page_number(Clubs.Search.BASE)
        self.response["results"] = self.__parse_search_results()

        return self.response
