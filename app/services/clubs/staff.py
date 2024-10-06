from dataclasses import dataclass
from datetime import datetime

from app.services.base import TransfermarktBase
from app.utils.regex import REGEX_STAFF_ID
from app.utils.utils import clean_response, extract_from_url, safe_regex
from app.utils.xpath import Clubs


@dataclass
class TransfermarktClubStaffs(TransfermarktBase):
    """
    A class for retrieving and parsing the staff members of a football club from Transfermarkt.

    Args:
        club_id (str): The unique identifier of the football club.
        URL (str): The URL template for the club's staff page on Transfermarkt.
    """

    club_id: str = None
    URL: str = "https://www.transfermarkt.us/-/mitarbeiter/verein/{club_id}/plus/1"

    def __post_init__(self) -> None:
        """Initialize the TransfermarktClubStaffs class."""
        self.URL = self.URL.format(club_id=self.club_id)
        self.page = self.request_url_page()
        self.raise_exception_if_not_found(xpath=Clubs.Staff.CLUB_NAME)

    def __parse_club_staffs(self) -> list[dict]:
        """
        Parse staff information from the webpage and return a list of dictionaries, each representing a staff member.

        Returns:
            list[dict]: A list of staff information dictionaries.
        """
        staffs_ids = [
            safe_regex(ids, REGEX_STAFF_ID, "id") for ids in self.get_list_by_xpath(Clubs.Staff.ID)
        ]
        staffs_names = self.page.xpath(Clubs.Staff.NAME)
        staffs_jobs = self.page.xpath(Clubs.Players.PAGE_INFOS)
        staffs_ages = self.page.xpath(Clubs.Staff.AGE)
        staffs_nationalities = self.page.xpath(Clubs.Staff.NATIONALITIES)
        staffs_appointed = self.page.xpath(Clubs.Staff.APPOINTED)
        staffs_contracts = self.page.xpath(Clubs.Staff.CONTRACT)
        staffs_last_club = self.page.xpath(Clubs.Staff.LAST_CLUB)

        return [
            {
                "id": idx,
                "name": name,
                "job": job,
                "age": age,
                "nationality": nationality,
                "appointed": appointed,
                "contract": contract,
                "lastClub": last_club,
            }
            for idx, name, job, age, nationality, appointed, contract, last_club in zip(  # noqa: E501
                staffs_ids,
                staffs_names,
                staffs_jobs,
                staffs_ages,
                staffs_nationalities,
                staffs_appointed,
                staffs_contracts,
                staffs_last_club,
            )
        ]

    def get_club_staffs(self) -> dict:
        """
        Retrieve and parse staff information for the specified football club.

        Returns:
            dict: A dictionary containing the club's unique identifier, staff information, and the timestamp of when
                  the data was last updated.
        """
        self.response["id"] = self.club_id
        self.response["staffs"] = self.__parse_club_staffs()
        self.response["updatedAt"] = datetime.now()

        return clean_response(self.response)
