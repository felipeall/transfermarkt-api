from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.utils import extract_from_url
from app.utils.xpath import Competitions


@dataclass
class TransfermarktCompetitionClubs(TransfermarktBase):
    competition_id: str = None
    season_id: str = None
    URL: str = "https://www.transfermarkt.com/-/startseite/wettbewerb/{competition_id}/plus/?saison_id={season_id}"

    def __post_init__(self):
        self.URL = self.URL.format(competition_id=self.competition_id, season_id=self.season_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Competitions.Profile.NAME)

    def __parse_competition_clubs(self) -> list:
        urls = self.get_list_by_xpath(Competitions.Clubs.URLS)
        names = self.get_list_by_xpath(Competitions.Clubs.NAMES)
        ids = [extract_from_url(url) for url in urls]

        return [{"id": idx, "name": name} for idx, name in zip(ids, names)]

    def get_competition_clubs(self) -> dict:
        self.response["id"] = self.competition_id
        self.response["name"] = self.get_text_by_xpath(Competitions.Profile.NAME)
        self.response["seasonID"] = extract_from_url(
            self.get_text_by_xpath(Competitions.Profile.URL),
            "season_id",
        )
        self.response["clubs"] = self.__parse_competition_clubs()
        self.response["updatedAt"] = datetime.now()

        return self.response
