from app.tfmkt import TfmktClient


async def group_achievements(tfmkt: TfmktClient, data: dict) -> list[dict]:
    """
    Group upstream achievement records (one per title won) into titles with a count and per-season details.

    Titles follow upstream's display order; details are most recent season first. Player records carry the club and
    competition of each title; club records carry only the season, so those fields are null.
    """
    records_by_title: dict[int, list[dict]] = {}
    for record in data.get("achievements") or []:
        records_by_title.setdefault(record["id"], []).append(record)

    aggregated = {entry["id"]: entry for entry in data.get("aggregated") or []}
    titles = sorted(
        records_by_title,
        key=lambda title_id: ((aggregated.get(title_id) or {}).get("order", 10_000), title_id),
    )

    details = [record.get("details") or {} for records in records_by_title.values() for record in records]
    clubs = await tfmkt.clubs(d.get("clubId") for d in details if d.get("clubId") not in (None, "", "0"))
    competitions = await tfmkt.competitions(d.get("competitionId") for d in details if d.get("competitionId"))

    def entity(entities: dict, entity_id: str | int | None) -> dict | None:
        """Return `{id, name}` for a referenced club or competition, or None when there is no reference."""
        if entity_id in (None, "", "0"):
            return None
        return {"id": str(entity_id), "name": entities.get(str(entity_id), {}).get("name")}

    return [
        {
            "title": (
                (aggregated.get(title_id) or {}).get("name") or records_by_title[title_id][0].get("name") or ""
            ).strip(),
            "count": len(records_by_title[title_id]),
            "details": [
                {
                    "season": {
                        "id": str(record["seasonId"]) if record.get("seasonId") is not None else None,
                        "name": (record.get("season") or {}).get("display"),
                    },
                    "club": entity(clubs, (record.get("details") or {}).get("clubId")),
                    "competition": entity(competitions, (record.get("details") or {}).get("competitionId")),
                }
                for record in sorted(records_by_title[title_id], key=lambda r: r.get("seasonId") or 0, reverse=True)
            ],
        }
        for title_id in titles
    ]
