import asyncio

from app.tfmkt import TfmktClient
from app.tfmkt.reference import market_value_of


async def get_player_market_value(tfmkt: TfmktClient, player_id: str) -> dict:
    """
    Current market value, valuation history (oldest first) and worldwide market-value ranking.

    Club names are the clubs' current names. Only the worldwide ranking is available upstream; the v3 position,
    club and country rankings have no JSON source.
    """
    data, ranking = await asyncio.gather(
        tfmkt.player_market_value_history(player_id),
        tfmkt.player_market_value_ranking(player_id),
    )
    history = sorted(data.get("history") or [], key=lambda e: (e.get("marketValue") or {}).get("determined") or "")
    clubs = await tfmkt.clubs(entry.get("clubId") for entry in history)
    worldwide = (ranking or {}).get("ranking")

    return {
        "id": player_id,
        "marketValue": market_value_of((data.get("current") or {}).get("marketValue")),
        "marketValueHistory": [
            {
                "age": entry.get("age"),
                "date": (entry.get("marketValue") or {}).get("determined"),
                "clubId": str(entry["clubId"]) if entry.get("clubId") else None,
                "clubName": clubs.get(str(entry.get("clubId")), {}).get("name"),
                "marketValue": market_value_of(entry.get("marketValue")),
            }
            for entry in history
        ],
        "ranking": {"Worldwide": worldwide} if worldwide else None,
    }
