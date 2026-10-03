from app.tfmkt import TfmktClient
from app.tfmkt.reference import market_value_of


async def get_player_market_value(tfmkt: TfmktClient, player_id: str) -> dict:
    """Current market value and valuation history, oldest first. Club names are the clubs' current names."""
    data = await tfmkt.player_market_value_history(player_id)
    history = sorted(data.get("history") or [], key=lambda e: (e.get("marketValue") or {}).get("determined") or "")
    clubs = await tfmkt.clubs(entry.get("clubId") for entry in history)

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
    }
