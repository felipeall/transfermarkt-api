"""Typed async facade over the upstream assembly services."""

from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any, NoReturn, Self, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from transfermarkt_api.cache import CacheConfig
from transfermarkt_api.exceptions import EndpointUnavailable, UpstreamError
from transfermarkt_api.schemas import (
    Achievements,
    ClubListing,
    ClubPlayers,
    ClubProfile,
    ClubSearch,
    CoachProfile,
    CoachSearch,
    CompetitionClubs,
    CompetitionSearch,
    CompetitionSeasons,
    CompetitionTable,
    Countries,
    Game,
    PlayerAbsences,
    PlayerInjuries,
    PlayerMarketValue,
    PlayerMatches,
    PlayerNationalCareer,
    PlayerProfile,
    PlayerSearch,
    PlayerStats,
    PlayerTransfers,
)
from transfermarkt_api.services import countries
from transfermarkt_api.services.clubs import achievements as club_achievements
from transfermarkt_api.services.clubs import listing as club_listing
from transfermarkt_api.services.clubs import players as club_players
from transfermarkt_api.services.clubs import profile as club_profile
from transfermarkt_api.services.clubs import search as club_search
from transfermarkt_api.services.coaches import profile as coach_profile
from transfermarkt_api.services.coaches import search as coach_search
from transfermarkt_api.services.competitions import clubs as competition_clubs
from transfermarkt_api.services.competitions import search as competition_search
from transfermarkt_api.services.competitions import seasons as competition_seasons
from transfermarkt_api.services.competitions import table as competition_table
from transfermarkt_api.services.games import game
from transfermarkt_api.services.players import absences as player_absences
from transfermarkt_api.services.players import achievements as player_achievements
from transfermarkt_api.services.players import injuries as player_injuries
from transfermarkt_api.services.players import market_value as player_market_value
from transfermarkt_api.services.players import matches as player_matches
from transfermarkt_api.services.players import national_career as player_national_career
from transfermarkt_api.services.players import profile as player_profile
from transfermarkt_api.services.players import search as player_search
from transfermarkt_api.services.players import stats as player_stats
from transfermarkt_api.services.players import transfers as player_transfers
from transfermarkt_api.tfmkt import TfmktClient
from transfermarkt_api.tfmkt.freshness import fetch_scope

Model = TypeVar("Model", bound=BaseModel)


class Transfermarkt:
    """Async data client; owns its transport and supports one event loop per instance."""

    def __init__(
        self,
        *,
        base_url: str = "https://tmapi.transfermarkt.technology",
        timeout: float | httpx.Timeout | None = 15.0,
        max_concurrency: int = 10,
        transport: httpx.AsyncBaseTransport | None = None,
        cache: CacheConfig | None = CacheConfig(),
    ) -> None:
        """Configure upstream access; cache=None disables ordinary and reference caching."""
        self._client = TfmktClient(
            base_url=base_url,
            timeout=timeout,
            max_concurrency=max_concurrency,
            transport=transport,
            cache=cache,
        )

    async def __aenter__(self) -> Self:
        """Enter this client's lifetime without making a request."""
        if self._client.http.is_closed:
            raise RuntimeError("Transfermarkt client is closed")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the owned transport, including when the body raises."""
        await self.aclose()

    async def aclose(self) -> None:
        """Close the owned HTTP client and transport; safe to call more than once."""
        await self._client.aclose()

    async def _call(self, model: type[Model], service: Callable[..., Awaitable[dict]], *args: Any) -> Model:
        with fetch_scope():
            data = await service(self._client, *args)
            try:
                return model.model_validate(data)
            except ValidationError as error:
                raise UpstreamError(f"Unexpected upstream payload for {model.__name__}") from error

    async def countries(self) -> Countries:
        """List country metadata, including historical entries."""
        return await self._call(Countries, countries.list_countries)

    async def clubs(self, country_id: int) -> ClubListing:
        """List the available clubs for a country."""
        _positive_integer(country_id, "country_id")
        return await self._call(ClubListing, club_listing.list_clubs, country_id)

    async def search_clubs(self, club_name: str, *, page_number: int = 1) -> ClubSearch:
        """Search clubs, returning one page."""
        _positive_integer(page_number, "page_number")
        return await self._call(ClubSearch, club_search.search_clubs, club_name, page_number)

    async def club_profile(self, club_id: str) -> ClubProfile:
        """Get a club's profile."""
        return await self._call(ClubProfile, club_profile.get_club_profile, club_id)

    async def club_players(self, club_id: str, *, season_id: str | None = None) -> ClubPlayers:
        """Get the current or historical squad of a club."""
        return await self._call(ClubPlayers, club_players.get_club_players, club_id, season_id)

    async def club_achievements(self, club_id: str) -> Achievements:
        """Get a club's titles."""
        return await self._call(Achievements, club_achievements.get_club_achievements, club_id)

    async def search_players(self, player_name: str, *, page_number: int = 1) -> PlayerSearch:
        """Search players, returning one page."""
        _positive_integer(page_number, "page_number")
        return await self._call(PlayerSearch, player_search.search_players, player_name, page_number)

    async def player_profile(self, player_id: str) -> PlayerProfile:
        """Get a player's profile."""
        return await self._call(PlayerProfile, player_profile.get_player_profile, player_id)

    async def player_market_value(self, player_id: str) -> PlayerMarketValue:
        """Get current and historical player valuations."""
        return await self._call(PlayerMarketValue, player_market_value.get_player_market_value, player_id)

    async def player_transfers(self, player_id: str) -> PlayerTransfers:
        """Get a player's transfer history."""
        return await self._call(PlayerTransfers, player_transfers.get_player_transfers, player_id)

    async def player_stats(self, player_id: str) -> PlayerStats:
        """Get a player's club statistics by season and competition."""
        return await self._call(PlayerStats, player_stats.get_player_stats, player_id)

    async def player_matches(
        self, player_id: str, *, season_id: str | None = None, page_number: int = 1
    ) -> PlayerMatches:
        """Get one page of past matches, optionally filtered by season."""
        _positive_integer(page_number, "page_number")
        return await self._call(PlayerMatches, player_matches.get_player_matches, player_id, page_number, season_id)

    async def player_injuries(self, player_id: str, *, page_number: int = 1) -> PlayerInjuries:
        """Get one page of a player's injuries."""
        _positive_integer(page_number, "page_number")
        return await self._call(PlayerInjuries, player_injuries.get_player_injuries, player_id, page_number)

    async def player_absences(self, player_id: str, *, page_number: int = 1) -> PlayerAbsences:
        """Get one page of a player's non-injury absences."""
        _positive_integer(page_number, "page_number")
        return await self._call(PlayerAbsences, player_absences.get_player_absences, player_id, page_number)

    async def player_achievements(self, player_id: str) -> Achievements:
        """Get a player's titles and awards."""
        return await self._call(Achievements, player_achievements.get_player_achievements, player_id)

    async def player_national_career(self, player_id: str) -> PlayerNationalCareer:
        """Get a player's senior and youth national teams."""
        return await self._call(PlayerNationalCareer, player_national_career.get_player_national_career, player_id)

    async def search_coaches(self, coach_name: str, *, page_number: int = 1) -> CoachSearch:
        """Search coaches, returning one page."""
        _positive_integer(page_number, "page_number")
        return await self._call(CoachSearch, coach_search.search_coaches, coach_name, page_number)

    async def coach_profile(self, coach_id: str) -> CoachProfile:
        """Get a coach's profile."""
        return await self._call(CoachProfile, coach_profile.get_coach_profile, coach_id)

    async def search_competitions(self, competition_name: str, *, page_number: int = 1) -> CompetitionSearch:
        """Search competitions, returning one page."""
        _positive_integer(page_number, "page_number")
        return await self._call(
            CompetitionSearch, competition_search.search_competitions, competition_name, page_number
        )

    async def competition_clubs(self, competition_id: str, *, season_id: str | None = None) -> CompetitionClubs:
        """Get the clubs in a competition season."""
        return await self._call(CompetitionClubs, competition_clubs.get_competition_clubs, competition_id, season_id)

    async def competition_table(self, competition_id: str, *, season_id: str | None = None) -> CompetitionTable:
        """Get the league or group tables in a competition season."""
        return await self._call(CompetitionTable, competition_table.get_competition_table, competition_id, season_id)

    async def competition_seasons(self, competition_id: str) -> CompetitionSeasons:
        """Get the available seasons for a competition."""
        return await self._call(CompetitionSeasons, competition_seasons.get_competition_seasons, competition_id)

    async def game(self, game_id: str) -> Game:
        """Get match details, lineups, statistics and events."""
        return await self._call(Game, game.get_game, game_id)

    async def player_jersey_numbers(self, player_id: str) -> NoReturn:
        """Raise EndpointUnavailable: upstream provides no jersey-number history."""
        raise EndpointUnavailable(
            "Jersey number history is not available: Transfermarkt's JSON API has no equivalent data."
        )


def _positive_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
