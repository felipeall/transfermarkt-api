"""Endpoint cases shared by the fixture capture script and the offline snapshot tests."""

# (snapshot name, request path)
CASES: list[tuple[str, str]] = [
    # Players
    ("players_search_messi", "/players/search/messi"),
    ("players_28003_profile", "/players/28003/profile"),
    ("players_0_profile", "/players/0/profile"),
    ("players_17259_profile", "/players/17259/profile"),
    ("players_5023_profile", "/players/5023/profile"),
    ("players_8198_profile", "/players/8198/profile"),
    ("players_28003_market_value", "/players/28003/market_value"),
    ("players_17259_market_value", "/players/17259/market_value"),
    ("players_28003_transfers", "/players/28003/transfers"),
    ("players_5023_transfers", "/players/5023/transfers"),
    ("players_28003_jersey_numbers", "/players/28003/jersey_numbers"),
    ("players_28003_stats", "/players/28003/stats"),
    ("players_17259_stats", "/players/17259/stats"),
    ("players_28003_injuries", "/players/28003/injuries"),
    ("players_28003_achievements", "/players/28003/achievements"),
    # Clubs
    ("clubs_search_barcelona", "/clubs/search/barcelona"),
    ("clubs_131_profile", "/clubs/131/profile"),
    ("clubs_3331_profile", "/clubs/3331/profile"),
    ("clubs_3383_profile", "/clubs/3383/profile"),
    ("clubs_131_players", "/clubs/131/players"),
    ("clubs_131_players_2014", "/clubs/131/players?season_id=2014"),
    ("clubs_27_players_2024", "/clubs/27/players?season_id=2024"),
    # Competitions
    ("competitions_search_premier_league", "/competitions/search/premier%20league"),
    ("competitions_GB1_clubs", "/competitions/GB1/clubs"),
    ("competitions_ES1_clubs_2014", "/competitions/ES1/clubs?season_id=2014"),
]
