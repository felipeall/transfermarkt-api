from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from lxml import etree
from requests import Response
from requests.exceptions import (
    ConnectionError as RequestsConnectionError,
    Timeout,
    TooManyRedirects,
)

from app.utils.utils import trim
from app.utils.xpath import Pagination


@dataclass
class TransfermarktBase:
    """
    Base class for making HTTP requests to Transfermarkt and extracting
    data from web pages.

    Args:
        URL: The URL for the web page to fetch.

    Attributes:
        page: The parsed web page content.
        response: A dictionary used to build the API response.
    """

    URL: str
    page: ElementTree = field(default_factory=lambda: None, init=False)
    response: dict = field(default_factory=lambda: {}, init=False)

    def make_request(self, url: Optional[str] = None) -> Response:
        """
        Make an HTTP GET request to Transfermarkt.

        Raises:
            HTTPException: When the request times out, cannot connect,
            redirects excessively, or returns an error status.
        """

        request_url = self.URL if not url else url

        try:
            response = requests.get(
                url=request_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": (
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,image/avif,"
                        "image/webp,*/*;q=0.8"
                    ),
                    "Accept-Language": "en-GB,en;q=0.9",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                },
                timeout=30,
                allow_redirects=True,
            )
        except TooManyRedirects as error:
            raise HTTPException(
                status_code=502,
                detail=f"Too many redirects for URL: {request_url}",
            ) from error
        except Timeout as error:
            raise HTTPException(
                status_code=504,
                detail=f"Request timed out for URL: {request_url}",
            ) from error
        except RequestsConnectionError as error:
            raise HTTPException(
                status_code=502,
                detail=f"Connection error for URL: {request_url}",
            ) from error
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail=f"Request error for URL: {request_url}. {error}",
            ) from error
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error for URL: {request_url}. {error}",
            ) from error

        if 400 <= response.status_code < 500:
            raise HTTPException(
                status_code=response.status_code,
                detail=(
                    f"Client error: {response.reason} "
                    f"for URL: {request_url}"
                ),
            )

        if 500 <= response.status_code < 600:
            raise HTTPException(
                status_code=response.status_code,
                detail=(
                    f"Server error: {response.reason} "
                    f"for URL: {request_url}"
                ),
            )

        return response

    def request_url_bsoup(self) -> BeautifulSoup:
        """
        Fetch and parse a Transfermarkt page using BeautifulSoup.

        For player-stat requests, diagnostic response information is logged
        and the raw HTML is saved inside the Docker container under /tmp.
        """

        response = self.make_request()

        soup = BeautifulSoup(
            markup=response.content,
            features="html.parser",
        )

        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else None
        )

        diagnostic = {
            "requested_url": self.URL,
            "final_url": str(response.url),
            "status": response.status_code,
            "content_type": response.headers.get("content-type"),
            "content_length": len(response.content),
            "title": title,
        }

        print(
            {
                "transfermarkt_response": diagnostic,
            },
            flush=True,
        )

        # Save raw HTML only for player-stat requests.
        if "leistungsdatendetails" in self.URL:
            player_id = (
                self.URL
                .rstrip("/")
                .split("/")[-1]
                .split("?")[0]
            )

            debug_path = Path(
                f"/tmp/transfermarkt-stats-{player_id}.html"
            )

            try:
                debug_path.write_bytes(response.content)

                print(
                    {
                        "stats_debug_html": str(debug_path),
                    },
                    flush=True,
                )
            except OSError as error:
                print(
                    {
                        "stats_debug_write_error": str(error),
                    },
                    flush=True,
                )

            page_text = soup.get_text(
                separator=" ",
                strip=True,
            )

            print(
                {
                    "stats_page_text_preview": page_text[:500],
                },
                flush=True,
            )

        return soup

    @staticmethod
    def convert_bsoup_to_page(
        bsoup: BeautifulSoup,
    ) -> ElementTree:
        """
        Convert a BeautifulSoup document to an lxml ElementTree.
        """

        return etree.HTML(str(bsoup))

    def request_url_page(self) -> ElementTree:
        """
        Fetch, parse, and convert the page to an ElementTree.
        """

        bsoup = self.request_url_bsoup()

        return self.convert_bsoup_to_page(
            bsoup=bsoup,
        )

    def raise_exception_if_not_found(
        self,
        xpath: str,
    ) -> None:
        """
        Raise an HTTP 404 when the supplied XPath matches nothing.
        """

        if not self.get_text_by_xpath(xpath):
            raise HTTPException(
                status_code=404,
                detail=f"Invalid request (URL: {self.URL})",
            )

    def get_list_by_xpath(
        self,
        xpath: str,
        remove_empty: Optional[bool] = True,
    ) -> list:
        """
        Return all values matching an XPath expression.
        """

        elements = self.page.xpath(xpath)

        if remove_empty:
            elements_valid = [
                trim(element)
                for element in elements
                if trim(element)
            ]
        else:
            elements_valid = [
                trim(element)
                for element in elements
            ]

        return elements_valid or []

    def get_text_by_xpath(
        self,
        xpath: str,
        pos: int = 0,
        iloc: Optional[int] = None,
        iloc_from: Optional[int] = None,
        iloc_to: Optional[int] = None,
        join_str: Optional[str] = None,
    ) -> Optional[str]:
        """
        Extract text content using an XPath expression.
        """

        element = self.page.xpath(xpath)

        if not element:
            return None

        if isinstance(element, list):
            element = [
                trim(item)
                for item in element
                if trim(item)
            ]

        if isinstance(iloc, int):
            try:
                element = element[iloc]
            except IndexError:
                return None

        if (
            isinstance(iloc_from, int)
            and isinstance(iloc_to, int)
        ):
            element = element[iloc_from:iloc_to]
        elif isinstance(iloc_to, int):
            element = element[:iloc_to]
        elif isinstance(iloc_from, int):
            element = element[iloc_from:]

        if isinstance(join_str, str):
            if not isinstance(element, list):
                return trim(element)

            return join_str.join(
                trim(item)
                for item in element
            )

        try:
            return trim(element[pos])
        except (IndexError, TypeError):
            return None

    def get_last_page_number(
        self,
        xpath_base: str = "",
    ) -> int:
        """
        Return the final page number for a paginated result.
        """

        for xpath in [
            Pagination.PAGE_NUMBER_LAST,
            Pagination.PAGE_NUMBER_ACTIVE,
        ]:
            url_page = self.get_text_by_xpath(
                xpath_base + xpath,
            )

            if url_page:
                return int(
                    url_page
                    .split("=")[-1]
                    .split("/")[-1]
                )

        return 1