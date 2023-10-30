from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from schema import And, Optional, Schema

from app.services.clubs.profile import TransfermarktClubProfile


def test_get_club_profile_not_found():
    with pytest.raises(HTTPException):
        TransfermarktClubProfile(club_id="0")


@pytest.mark.parametrize("club_id", ["210", "131", "31", "27", "5"])
@patch("app.utils.utils.clean_response", side_effect=lambda x: x)
def test_get_club_profile(
    mock_clean_response,
    club_id,
    regex_club_url,
    regex_date_mmm_dd_yyyy,
    regex_market_value,
    regex_value_variation,
    regex_integer,
    len_greater_than_0,
):
    tfmkt = TransfermarktClubProfile(club_id=club_id)
    result = tfmkt.get_club_profile()

    expected_schema = Schema(
        {
            "id": And(str, len_greater_than_0),
            "url": And(str, len_greater_than_0, regex_club_url),
            "name": And(str, len_greater_than_0),
            "officialName": And(str, len_greater_than_0),
            "image": And(str, len_greater_than_0),
            Optional("legalForm"): And(str, len_greater_than_0),
            "addressLine1": And(str, len_greater_than_0),
            "addressLine2": And(str, len_greater_than_0),
            "addressLine3": And(str, len_greater_than_0),
            "tel": And(str, len_greater_than_0),
            "fax": And(str, len_greater_than_0),
            "website": And(str, len_greater_than_0),
            "foundedOn": And(str, len_greater_than_0, regex_date_mmm_dd_yyyy),
            Optional("members"): And(str, len_greater_than_0),
            Optional("membersDate"): And(str, len_greater_than_0, regex_date_mmm_dd_yyyy),
            Optional("otherSports"): list,
            Optional("colors"): list,
            "stadiumName": And(str, len_greater_than_0),
            "stadiumSeats": And(str, len_greater_than_0, regex_integer),
            "currentTransferRecord": And(str, len_greater_than_0, regex_value_variation),
            "currentMarketValue": And(str, len_greater_than_0, regex_market_value),
            Optional("confederation"): str,
            Optional("fifaWorldRanking"): str,
            "squad": {
                "size": And(str, len_greater_than_0),
                "averageAge": And(str, len_greater_than_0),
                "foreigners": And(str, len_greater_than_0),
                "nationalTeamPlayers": And(str, len_greater_than_0),
            },
            "league": {
                "id": And(str, len_greater_than_0),
                "name": And(str, len_greater_than_0),
                "countryID": And(str, len_greater_than_0),
                "countryName": And(str, len_greater_than_0),
                "tier": And(str, len_greater_than_0),
            },
            Optional("historicalCrests"): list,
            "updatedAt": datetime,
        },
    )

    assert expected_schema.validate(result)
