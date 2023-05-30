from dataclasses import dataclass, field

from fastapi import HTTPException

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_list_by_xpath,
    get_text_by_xpath,
    remove_str,
    request_url_page,
    safe_regex,
    safe_split,
)
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubProfile:
    club_id: str
    club_profile: dict = field(default_factory=lambda: {})

    def get_club_profile(self):
        self._request_page()

        self.club_profile["id"] = self.club_id
        self.club_profile["url"] = get_text_by_xpath(self, Clubs.Profile.URL)
        self._check_club_found()
        self.club_profile["name"] = get_text_by_xpath(self, Clubs.Profile.NAME)
        self.club_profile["officialName"] = get_text_by_xpath(self, Clubs.Profile.NAME_OFFICIAL)
        self.club_profile["image"] = safe_split(get_text_by_xpath(self, Clubs.Profile.IMAGE), "?")[0]
        self.club_profile["legalForm"] = get_text_by_xpath(self, Clubs.Profile.LEGAL_FORM)
        self.club_profile["addressLine1"] = get_text_by_xpath(self, Clubs.Profile.ADDRESS_LINE_1)
        self.club_profile["addressLine2"] = get_text_by_xpath(self, Clubs.Profile.ADDRESS_LINE_2)
        self.club_profile["addressLine3"] = get_text_by_xpath(self, Clubs.Profile.ADDRESS_LINE_3)
        self.club_profile["tel"] = get_text_by_xpath(self, Clubs.Profile.TEL)
        self.club_profile["fax"] = get_text_by_xpath(self, Clubs.Profile.FAX)
        self.club_profile["website"] = get_text_by_xpath(self, Clubs.Profile.WEBSITE)
        self.club_profile["foundedOn"] = get_text_by_xpath(self, Clubs.Profile.FOUNDED_ON)
        self.club_profile["members"] = get_text_by_xpath(self, Clubs.Profile.MEMBERS)
        self.club_profile["membersDate"] = remove_str(
            get_text_by_xpath(self, Clubs.Profile.MEMBERS_DATE, pos=1), ["(", "Score", ":", ")"]
        )
        self.club_profile["otherSports"] = safe_split(get_text_by_xpath(self, Clubs.Profile.OTHER_SPORTS), ",")
        self.club_profile["colors"] = [
            remove_str(e, ["background-color:", ";"]) for e in get_list_by_xpath(self, Clubs.Profile.COLORS) if "#" in e
        ]

        self.club_profile["stadiumName"] = get_text_by_xpath(self, Clubs.Profile.STADIUM_NAME)
        self.club_profile["stadiumSeats"] = remove_str(get_text_by_xpath(self, Clubs.Profile.STADIUM_SEATS), "Seats")

        self.club_profile["currentTransferRecord"] = get_text_by_xpath(self, Clubs.Profile.TRANSFER_RECORD)
        self.club_profile["currentMarketValue"] = get_text_by_xpath(
            self, Clubs.Profile.MARKET_VALUE, iloc=-2, join_str=""
        )

        self.club_profile["confederation"] = get_text_by_xpath(self, Clubs.Profile.CONFEDERATION)
        self.club_profile["fifaWorldRanking"] = remove_str(get_text_by_xpath(self, Clubs.Profile.RANKING), "Pos")

        self.club_profile["squad"] = {
            "size": get_text_by_xpath(self, Clubs.Profile.SQUAD_SIZE),
            "averageAge": get_text_by_xpath(self, Clubs.Profile.SQUAD_AVG_AGE),
            "foreigners": get_text_by_xpath(self, Clubs.Profile.SQUAD_FOREIGNERS),
            "nationalTeamPlayers": get_text_by_xpath(self, Clubs.Profile.SQUAD_NATIONAL_PLAYERS),
        }

        self.club_profile["league"] = {
            "id": extract_from_url(get_text_by_xpath(self, Clubs.Profile.LEAGUE_ID)),
            "name": get_text_by_xpath(self, Clubs.Profile.LEAGUE_NAME),
            "countryID": safe_regex(get_text_by_xpath(self, Clubs.Profile.LEAGUE_COUNTRY_ID), r"(?P<id>\d)", "id"),
            "countryName": get_text_by_xpath(self, Clubs.Profile.LEAGUE_COUNTRY_NAME),
            "tier": get_text_by_xpath(self, Clubs.Profile.LEAGUE_TIER),
        }

        self.club_profile["historicalCrests"] = [
            safe_split(e, "?")[0] for e in get_list_by_xpath(self, Clubs.Profile.CRESTS_HISTORICAL)
        ]

        return clean_response(self.club_profile)

    def _request_page(self) -> None:
        player_url = f"https://www.transfermarkt.us/-/datenfakten/verein/{self.club_id}"
        self.page = request_url_page(url=player_url)

    def _check_club_found(self):
        if not self.club_profile["url"]:
            raise HTTPException(status_code=404, detail=f"Club Profile not found for id: {self.club_id}")
