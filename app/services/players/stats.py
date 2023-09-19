from dataclasses import dataclass, field
from datetime import datetime
from xml.etree import ElementTree

from fastapi import HTTPException

from app.utils.utils import (
    clean_response,
    extract_from_url,
    get_text_by_xpath,
    remove_str,
    request_url_page,
    trim,
)
from app.utils.xpath import Players


@dataclass
class TransfermarktPlayerStats:
    player_id: str
    player_stats: dict = field(default_factory=lambda: {})

    def __post_init__(self):
        self._request_player_page()
        self._check_player_found()
        self._check_player_goalkeeper()

    def get_player_stats(self) -> dict:
        self.player_stats["id"] = self.player_id
        self.player_stats["stats"] = (
            self.parse_player_stats_goalkeeper() if self.goalkeeper else self.parse_player_stats_field()
        )
        self.player_stats["lastUpdate"] = datetime.now()
        return clean_response(self.player_stats)

    def parse_player_stats_field(self) -> list:
        stats: list[ElementTree] = self.page.xpath(Players.Stats.PLAYER_STATS)

        seasons = [elem.text for elem in stats[::9]]
        competitions_ids = [
            extract_from_url(get_text_by_xpath(elem, Players.Stats.COMPETITIONS_IDS)) for elem in stats[2::9]
        ]
        competitions_names = [get_text_by_xpath(elem, Players.Stats.COMPETITIONS_NAMES) for elem in stats[2::9]]
        clubs_ids = [extract_from_url(get_text_by_xpath(elem, Players.Stats.CLUBS_IDS)) for elem in stats[3::9]]
        clubs_names = [get_text_by_xpath(elem, Players.Stats.CLUBS_NAMES) for elem in stats[3::9]]
        appearances = [get_text_by_xpath(elem, Players.Stats.APPEARANCES) for elem in stats[4::9]]
        goals = [elem.text for elem in stats[5::9]]
        assists = [elem.text for elem in stats[6::9]]
        cards = [trim(elem.text).split("/") for elem in stats[7::9]]
        yellow_cards = [card[0] for card in cards]
        second_yellow_cards = [card[1] for card in cards]
        red_cards = [card[2] for card in cards]
        minutes_played = [remove_str(trim(elem.text), ["'", "."]) for elem in stats[8::9]]

        return [
            {
                "season": season,
                "competitionID": competition_id,
                "competitionName": competition_name,
                "clubID": club_id,
                "clubName": club_name,
                "appearances": appearance,
                "goals": goal,
                "assists": assist,
                "yellowCards": yellow_card,
                "secondYellowCards": second_yellow_card,
                "redCards": red_card,
                "minutesPlayed": minute_played,
            }
            for season, competition_id, competition_name, club_id, club_name, appearance, goal, assist, yellow_card, second_yellow_card, red_card, minute_played in zip(  # noqa: E501
                seasons,
                competitions_ids,
                competitions_names,
                clubs_ids,
                clubs_names,
                appearances,
                goals,
                assists,
                yellow_cards,
                second_yellow_cards,
                red_cards,
                minutes_played,
            )
        ]


    def parse_player_stats_goalkeeper(self) -> list:
        stats: list[ElementTree] = self.page.xpath(Players.Stats.PLAYER_STATS)

        seasons = [elem.text for elem in stats[::10]]
        competitions_ids = [
            extract_from_url(get_text_by_xpath(elem, Players.Stats.COMPETITIONS_IDS)) for elem in stats[2::10]
        ]
        competitions_names = [get_text_by_xpath(elem, Players.Stats.COMPETITIONS_NAMES) for elem in stats[2::10]]
        clubs_ids = [extract_from_url(get_text_by_xpath(elem, Players.Stats.CLUBS_IDS)) for elem in stats[3::10]]
        clubs_names = [get_text_by_xpath(elem, Players.Stats.CLUBS_NAMES) for elem in stats[3::10]]
        appearances = [get_text_by_xpath(elem, Players.Stats.APPEARANCES) for elem in stats[4::10]]

        goals = [elem.text for elem in stats[5::10]]
        cards = [trim(elem.text).split("/") for elem in stats[6::10]]
        yellow_cards = [card[0] for card in cards]
        second_yellow_cards = [card[1] for card in cards]
        red_cards = [card[2] for card in cards]
        goals_conceded = [elem.text for elem in stats[7::10]]
        clean_sheets = [elem.text for elem in stats[8::10]]
        minutes_played = [remove_str(trim(elem.text), ["'", "."]) for elem in stats[9::10]]

        return [
            {
                "season": season,
                "competitionId": competition_id,
                "competitionName": competition_name,
                "clubId": club_id,
                "clubName": club_name,
                "appearances": appearance,
                "goals": goal,
                "yellowCards": yellow_card,
                "secondYellowCards": second_yellow_card,
                "redCards": red_card,
                "goalsConceded": red_card,
                "cleanSheets": red_card,
                "minutesPlayed": minute_played,
            }
            for season, competition_id, competition_name, club_id, club_name, appearance, goal, yellow_card, second_yellow_card, red_card, conceded, clean, minute_played in zip(  # noqa: E501
                seasons,
                competitions_ids,
                competitions_names,
                clubs_ids,
                clubs_names,
                appearances,
                goals,
                yellow_cards,
                second_yellow_cards,
                red_cards,
                goals_conceded,
                clean_sheets,
                minutes_played,
            )
        ]

    def _request_player_page(self) -> None:
        player_url = f"https://www.transfermarkt.com/-/leistungsdatendetails/spieler/{self.player_id}"
        self.page = request_url_page(url=player_url)

    def _check_player_found(self) -> None:
        if not get_text_by_xpath(self, Players.Profile.URL):
            raise HTTPException(status_code=404, detail=f"Player Stats not found for id: {self.player_id}")

    def _check_player_goalkeeper(self) -> None:
        self.goalkeeper = get_text_by_xpath(self, Players.Stats.GOALKEEPER) == "Goalkeeper"
