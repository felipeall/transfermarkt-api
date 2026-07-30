from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from fastapi import HTTPException

from app.services.base import TransfermarktBase


@dataclass
class TransfermarktPlayerStats(TransfermarktBase):
    """
    Retrieve player match performance data from Transfermarkt's JSON API
    and aggregate it by season, competition, and club.
    """

    player_id: str = None

    URL: str = (
        "https://tmapi.transfermarkt.technology/"
        "player/{player_id}/performance-game"
    )

    def __post_init__(self) -> None:
        self.URL = self.URL.format(
            player_id=self.player_id,
        )

    @staticmethod
    def _to_int(value: Any) -> int:
        if value is None:
            return 0

        if isinstance(value, bool):
            return int(value)

        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _get_season(game_information: dict) -> str:
        """
        Prefer Transfermarkt's display season, such as 25/26.

        Fall back to the numeric season ID when the display value
        is unavailable.
        """

        season = game_information.get("season") or {}

        return str(
            season.get("nonCyclicalName")
            or season.get("display")
            or game_information.get("seasonId")
            or "unknown"
        )

    @staticmethod
    def _get_competition_name(
        competition_id: str,
    ) -> str:
        """
        The performance-game endpoint does not include competition names.

        Use known names where available and fall back to the competition ID.
        """

        known_competitions = {
            "GB1": "Premier League",
            "L1": "Bundesliga",
            "ES1": "La Liga",
            "IT1": "Serie A",
            "FR1": "Ligue 1",
            "CL": "UEFA Champions League",
            "EL": "UEFA Europa League",
            "ECL": "UEFA Conference League",
            "FAC": "FA Cup",
            "CGB": "EFL Cup",
            "DFB": "DFB-Pokal",
            "CDR": "Copa del Rey",
            "CIT": "Coppa Italia",
            "CDF": "Coupe de France",
            "FIWC": "FIFA Club World Cup",
            "FS": "International Friendlies",
        }

        return known_competitions.get(
            competition_id,
            competition_id,
        )

    def _request_performance_data(self) -> List[dict]:
        response = self.make_request(
            url=self.URL,
        )

        try:
            payload = response.json()
        except ValueError as error:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Transfermarkt performance endpoint returned "
                    "invalid JSON"
                ),
            ) from error

        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Transfermarkt performance endpoint returned "
                    "an unexpected response"
                ),
            )

        if payload.get("success") is not True:
            raise HTTPException(
                status_code=502,
                detail=(
                    "Transfermarkt performance endpoint reported "
                    f"failure: {payload.get('message')}"
                ),
            )

        data = payload.get("data")

        if not isinstance(data, dict):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Transfermarkt performance response does not "
                    "contain a valid data object"
                ),
            )

        performance = data.get("performance")

        if not isinstance(performance, list):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Transfermarkt performance response does not "
                    "contain a performance list"
                ),
            )

        print(
            {
                "player_id": self.player_id,
                "performance_games": len(performance),
                "source_url": self.URL,
            },
            flush=True,
        )

        return performance

    def __parse_player_stats(self) -> List[dict]:
        games = self._request_performance_data()

        grouped: Dict[
            Tuple[str, str, str],
            dict,
        ] = {}

        processed_game_ids = set()

        for game in games:
            if not isinstance(game, dict):
                continue

            game_information = (
                game.get("gameInformation")
                or {}
            )

            clubs_information = (
                game.get("clubsInformation")
                or {}
            )

            statistics = game.get("statistics") or {}

            general_statistics = (
                statistics.get("generalStatistics")
                or {}
            )

            goal_statistics = (
                statistics.get("goalStatistics")
                or {}
            )

            card_statistics = (
                statistics.get("cardStatistics")
                or {}
            )

            playing_time_statistics = (
                statistics.get("playingTimeStatistics")
                or {}
            )

            game_id = str(
                game_information.get("gameId")
                or ""
            )

            if game_id and game_id in processed_game_ids:
                continue

            if game_id:
                processed_game_ids.add(game_id)

            competition_id = str(
                game_information.get("competitionId")
                or ""
            )

            club = clubs_information.get("club") or {}

            club_id = str(
                club.get("clubId")
                or general_statistics.get("primaryClubId")
                or ""
            )

            season_id = self._get_season(
                game_information,
            )

            if not competition_id or not club_id:
                continue

            # Only a played match counts as an appearance.
            if participation_state != "played":
                continue

            key = (
                season_id,
                competition_id,
                club_id,
            )

            if key not in grouped:
                grouped[key] = {
                    "competitionId": competition_id,
                    "competitionName": (
                        self._get_competition_name(
                            competition_id,
                        )
                    ),
                    "seasonId": season_id,
                    "clubId": club_id,
                    "appearances": 0,
                    "goals": 0,
                    "assists": 0,
                    "yellowCards": 0,
                    "redCards": 0,
                    "minutesPlayed": 0,
                }

            row = grouped[key]

            participation_state = (
                general_statistics.get(
                    "participationState"
                )
            )

            row["appearances"] += 1

            row["goals"] += self._to_int(
                goal_statistics.get(
                    "goalsScoredTotalOfficial"
                )
            )

            row["assists"] += self._to_int(
                goal_statistics.get(
                    "assistsOfficial"
                )
            )

            # yellowCardNet is 1 for a normal yellow and can be 0
            # when the player receives a second-yellow dismissal.
            row["yellowCards"] += self._to_int(
                card_statistics.get(
                    "yellowCardNet"
                )
            )

            has_red_card = bool(
                card_statistics.get("redCard")
                or card_statistics.get("yellowRedCard")
            )

            if has_red_card:
                row["redCards"] += 1

            row["minutesPlayed"] += self._to_int(
                playing_time_statistics.get(
                    "playedMinutes"
                )
            )

        results = list(grouped.values())

        results.sort(
            key=lambda row: (
                row["seasonId"],
                row["competitionId"],
                row["clubId"],
            ),
            reverse=True,
        )

        print(
            {
                "player_id": self.player_id,
                "aggregated_stat_rows": len(results),
            },
            flush=True,
        )

        return results

    def get_player_stats(self) -> dict:
        return {
            "updatedAt": datetime.now(
                timezone.utc
            ).isoformat(),
            "id": self.player_id,
            "stats": self.__parse_player_stats(),
        }