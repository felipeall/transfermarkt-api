from dataclasses import dataclass, field

from app.utils.utils import (
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    request_url_page,
)
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionClubs:
    competition_id: str
    season_id: str = None
    competition_clubs: dict = field(default_factory=lambda: {})

    def get_competition_clubs(self):
        self._request_page()

        self.competition_clubs["id"] = self.competition_id
        self.competition_clubs["name"] = get_text_by_xpath(self, Competitions.Profile.NAME)
        self.competition_clubs["seasonID"] = extract_from_url(
            get_text_by_xpath(self, Competitions.Profile.URL), "season_id"
        )
        self.competition_clubs["clubs"] = self._parse_competition_clubs()

        return self.competition_clubs

    def _request_page(self) -> None:
        url = f"https://www.transfermarkt.com/-/startseite/wettbewerb/{self.competition_id}"
        if self.season_id:
            url += f"/plus/?saison_id={self.season_id}"
        self.page = request_url_page(url=url)

    def _parse_competition_clubs(self):
        urls = get_list_by_xpath(self, Competitions.Clubs.URLS)
        names = get_list_by_xpath(self, Competitions.Clubs.NAMES)
        ids = [extract_from_url(url) for url in urls]

        return [{"id": idx, "name": name} for idx, name in zip(ids, names)]
