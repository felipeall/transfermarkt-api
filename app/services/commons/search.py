from dataclasses import dataclass
from xml.etree import ElementTree

from app.utils.utils import request_url_page


@dataclass
class TransfermarktSearch:
    query: str

    def __post_init__(self):
        search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={self.query}"
        self.search_page = request_url_page(url=search_url)
