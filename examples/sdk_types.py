"""A small consumer used to verify the SDK's exported type annotations."""

from typing import assert_type

from transfermarkt_api import CacheConfig, Transfermarkt
from transfermarkt_api.schemas import ClubPlayers, Countries
from transfermarkt_api.schemas.clubs.players import ClubPlayer


async def example() -> None:
    """Type-check facade results and nested response models."""
    async with Transfermarkt(cache=CacheConfig()) as tm:
        squad = await tm.club_players("985", season_id="2024")
        assert_type(squad, ClubPlayers)
        assert_type(squad.players[0], ClubPlayer)
        assert_type(await tm.countries(), Countries)
