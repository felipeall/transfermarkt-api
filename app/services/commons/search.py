from dataclasses import dataclass
from xml.etree import ElementTree

from app.utils.utils import request_url_page


@dataclass
class TransfermarktSearch:
    query: str
    search_page: ElementTree = None

    def _request_search_page(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}"
        self.search_page = request_url_page(url=search_url)
