import pytest
from schema import Regex


@pytest.fixture
def len_greater_than_0():
    return lambda x: len(x) > 0


@pytest.fixture
def len_equal_to_0():
    return lambda x: len(x) == 0


@pytest.fixture
def regex_club_url():
    return Regex(r"^/\w.+/startseite/verein/\d+$")


@pytest.fixture
def regex_date_mmm_dd_yyyy():
    return Regex(r"^(\w+\s\d+,\s\d+)|(-)$")


@pytest.fixture
def regex_market_value():
    return Regex(r"^(€\d+\.\d+.(m|bn))|(€\d+.k)|(-)$")


@pytest.fixture
def regex_value_variation():
    return Regex(r"^(\+|-)?€(\+|-)?(\d.+)(k|m)$")


@pytest.fixture
def regex_integer():
    return Regex(r"^(\d+|-)$")


@pytest.fixture
def regex_height():
    return Regex(r"^(\d+,\d+m)|(m)$")
