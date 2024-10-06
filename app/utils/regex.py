REGEX_DOB: str = r"^(?P<dob>.*)\s\((?P<age>\d*)\)"
REGEX_MEMBERS_DATE: str = r"\(Score: (?P<date>.+)\)"
REGEX_BG_COLOR: str = r"background-color:(?P<color>.+);"
REGEX_CHART_CLUB_ID: str = r"(?P<club_id>\d+)"
REGEX_COUNTRY_ID: str = r"(?P<id>\d+)"
REGEX_DOB_AGE: str = r"^(?P<dob>\w{3} \d{1,2}, \d{4}) \((?P<age>\d{2})\)"
REGEX_STAFF_ID: str = r'/small/(\d+)-'