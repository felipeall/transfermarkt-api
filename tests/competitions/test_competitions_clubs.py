import pytest
from fastapi import HTTPException

from app.services.competitions.clubs import TransfermarktCompetitionClubs


def test_competitions_clubs_id_0():
    tfmkt = TransfermarktCompetitionClubs(competition_id="0")

    with pytest.raises(HTTPException):
        tfmkt.get_competition_clubs()


def test_competitions_clubs_id_bra1_season_2023():
    tfmkt = TransfermarktCompetitionClubs(competition_id="BRA1", season_id="2023")
    result = tfmkt.get_competition_clubs()

    expected = {
        "id": "BRA1",
        "name": "Campeonato Brasileiro Série A",
        "seasonID": "2022",
        "clubs": [
            {"id": "1023", "name": "Sociedade Esportiva Palmeiras"},
            {"id": "614", "name": "CR Flamengo"},
            {"id": "679", "name": "Club Athletico Paranaense"},
            {"id": "585", "name": "São Paulo Futebol Clube"},
            {"id": "199", "name": "Sport Club Corinthians Paulista"},
            {"id": "330", "name": "Clube Atlético Mineiro"},
            {"id": "2462", "name": "Fluminense Football Club"},
            {"id": "8793", "name": "Red Bull Bragantino"},
            {"id": "537", "name": "Botafogo de Futebol e Regatas"},
            {"id": "210", "name": "Grêmio Foot-Ball Porto Alegrense"},
            {"id": "6600", "name": "Sport Club Internacional"},
            {"id": "978", "name": "Clube de Regatas Vasco da Gama"},
            {"id": "221", "name": "Santos FC"},
            {"id": "10010", "name": "Esporte Clube Bahia"},
            {"id": "609", "name": "Cruzeiro Esporte Clube"},
            {"id": "10870", "name": "Fortaleza Esporte Clube"},
            {"id": "776", "name": "Coritiba Foot Ball Club"},
            {"id": "2863", "name": "América Futebol Clube (MG)"},
            {"id": "3197", "name": "Goiás EC"},
            {"id": "28022", "name": "Cuiabá Esporte Clube (MT)"},
        ],
    }

    assert result == expected
