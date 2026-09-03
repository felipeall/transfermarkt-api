from datetime import date

import pytest

from app.schemas.players.market_value import MarketValueHistory


def history_entry(raw_date: str) -> MarketValueHistory:
    """Build a market-value history entry whose date comes straight from Transfermarkt."""
    return MarketValueHistory(
        age="20",
        date=raw_date,
        clubId="317",
        clubName="FC Twente Enschede",
        marketValue="€500k",
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Transfermarkt writes the market-value chart day-first. Both halves of
        # this pair come from the same player's chart; only the first is
        # ambiguous, and it used to be read as 6 March.
        ("03/06/2026", date(2026, 6, 3)),
        ("28/05/2025", date(2025, 5, 28)),
        # A day of 12 or under is where the swap used to happen, in both
        # directions.
        ("11/03/2026", date(2026, 3, 11)),
        ("02/12/2025", date(2025, 12, 2)),
        # Formats that name the month are not affected by dayfirst.
        ("Aug 15, 2014", date(2014, 8, 15)),
    ],
)
def test_parse_str_to_date_reads_transfermarkt_dates_day_first(raw, expected):
    """Dates are parsed day-first, as Transfermarkt writes them."""
    assert history_entry(raw).date == expected
