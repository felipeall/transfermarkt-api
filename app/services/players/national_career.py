from app.tfmkt import TfmktClient

CAREER_STATUS = {
    "CURRENT_NATIONAL_PLAYER": "current",
    "RECENT_NATIONAL_PLAYER": "recent",
    "FORMER_NATIONAL_PLAYER": "former",
}


async def get_player_national_career(tfmkt: TfmktClient, player_id: str) -> dict:
    """Senior and youth national teams the player has played for, in upstream order (most recent team first)."""
    history = (await tfmkt.player_national_career(player_id)).get("history") or []
    clubs = await tfmkt.clubs(entry.get("clubId") for entry in history)

    return {
        "id": player_id,
        "nationalTeams": [
            {
                "id": str(entry["clubId"]),
                "name": clubs.get(str(entry["clubId"]), {}).get("name"),
                "appearances": entry.get("gamesPlayed"),
                "goals": entry.get("goalsScored"),
                "shirtNumber": entry.get("shirtNumber"),
                "isCaptain": entry.get("isCaptain"),
                "debut": entry.get("debut"),
                "lastMatch": entry.get("lastGame"),
                "status": CAREER_STATUS.get(entry.get("careerState")),
            }
            for entry in history
        ],
    }
