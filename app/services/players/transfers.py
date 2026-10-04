import asyncio
import re
from typing import Optional

from app.tfmkt import TfmktClient
from app.tfmkt.reference import market_value_of, value_of

# upstream typeDetails.type -> transferType; STANDARD is split into transfer and freeTransfer by its fee label
TRANSFER_TYPES = {
    "STANDARD": "transfer",
    "INTERNAL_TRANSFER": "internal",
    "ACTIVE_LOAN_TRANSFER": "loan",
    "RETURNED_FROM_PREVIOUS_LOAN": "endOfLoan",
}

# formerClubsNote lists youth clubs as "Grandoli FC (1992-1995), Newell's Old Boys (1995-2000)"
YOUTH_CLUB_SEPARATOR = re.compile(r"(?<=\)),\s*")


async def get_player_transfers(tfmkt: TfmktClient, player_id: str) -> dict:
    """
    Transfer history, upcoming (pending) transfers first, then completed ones, most recent first.

    `fee` is null when upstream has no numeric fee: free transfers, loans without fee and unknown fees (`-`).
    `transferType` tells these apart: an unknown fee is a `transfer` with a null fee, never a `freeTransfer`.
    """
    player, history = await asyncio.gather(tfmkt.player(player_id), tfmkt.player_transfer_history(player_id))
    transfers = (history or {}).get("history") or {}
    records = (transfers.get("pending") or []) + (transfers.get("terminated") or [])
    clubs = await tfmkt.clubs(
        club_id
        for record in records
        for club_id in (record["transferSource"]["clubId"], record["transferDestination"]["clubId"])
    )

    def club(club_id: str | int) -> dict:
        """Return `{id, name}` for a club referenced by a transfer."""
        club_id = str(club_id)
        return {"id": club_id, "name": clubs.get(club_id, {}).get("name")}

    former_clubs_note = (player.get("attributes") or {}).get("formerClubsNote")

    return {
        "id": player_id,
        "transfers": [
            {
                "id": str(record["id"]),
                "clubFrom": club(record["transferSource"]["clubId"]),
                "clubTo": club(record["transferDestination"]["clubId"]),
                "date": (record["details"].get("date") or "")[:10] or None,
                "upcoming": bool(record["details"].get("isPending")),
                "transferType": transfer_type(record),
                "season": (record["details"].get("season") or {}).get("display"),
                "marketValue": market_value_of(record["details"].get("marketValue")),
                "fee": value_of(record["details"].get("fee")),
            }
            for record in records
        ],
        "youthClubs": YOUTH_CLUB_SEPARATOR.split(former_clubs_note) if former_clubs_note else [],
    }


def transfer_type(record: dict) -> Optional[str]:
    """Kind of transfer, or None for an upstream type this API does not know."""
    kind = TRANSFER_TYPES.get((record.get("typeDetails") or {}).get("type"))
    fee_label = ((record["details"].get("fee") or {}).get("compact") or {}).get("content") or ""
    if kind == "transfer" and fee_label.strip().lower() == "free transfer":
        return "freeTransfer"
    return kind
