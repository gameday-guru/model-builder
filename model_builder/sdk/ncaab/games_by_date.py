from datetime import datetime
from typing import Any, Callable, Dict, List, Protocol, TypeVar, cast

import requests
from dotenv import dotenv_values
from pydantic import BaseModel


class Periodlike(BaseModel):
    period_id: int
    game_id: int
    number: int
    name: str
    type: str
    away_score: int
    home_score: int

class GamesByDatelike(BaseModel):
    game_id: int
    season: int
    season_type: int
    status: str
    day: datetime
    date_time: datetime
    away_team: str
    home_team: str
    away_team_id: int
    home_team_id: int
    away_team_score: int
    home_team_score: int
    updated: datetime
    period: str
    time_remaining_minutes: None
    time_remaining_seconds: None
    point_spread: float
    over_under: float
    away_team_money_line: int
    home_team_money_line: int
    global_game_id: int
    global_away_team_id: int
    global_home_team_id: int
    tournament_id: None
    bracket: None
    round: None
    away_team_seed: None
    home_team_seed: None
    away_team_previous_game_id: None
    home_team_previous_game_id: None
    away_team_previous_global_game_id: None
    home_team_previous_global_game_id: None
    tournament_display_order: None
    tournament_display_order_for_home_team: str
    is_closed: bool
    game_end_date_time: datetime
    home_rotation_number: None
    away_rotation_number: None
    top_team_previous_game_id: None
    bottom_team_previous_game_id: None
    channel: None
    neutral_venue: None
    away_point_spread_payout: None
    home_point_spread_payout: None
    over_payout: None
    under_payout: None
    date_time_utc: datetime
    stadium: None
    periods: List[Periodlike]
    
class Period(BaseModel):
    period_id: int
    game_id: int
    number: int
    name: str
    type: str
    away_score: int
    home_score: int

class GameByDate(BaseModel):
    game_id: int
    season: int
    season_type: int
    status: str
    day: datetime
    date_time: datetime
    away_team: str
    home_team: str
    away_team_id: int
    home_team_id: int
    away_team_score: int
    home_team_score: int
    updated: datetime
    period: str
    time_remaining_minutes: None
    time_remaining_seconds: None
    point_spread: float
    over_under: float
    away_team_money_line: int
    home_team_money_line: int
    global_game_id: int
    global_away_team_id: int
    global_home_team_id: int
    tournament_id: None
    bracket: None
    round: None
    away_team_seed: None
    home_team_seed: None
    away_team_previous_game_id: None
    home_team_previous_game_id: None
    away_team_previous_global_game_id: None
    home_team_previous_global_game_id: None
    tournament_display_order: None
    tournament_display_order_for_home_team: str
    is_closed: bool
    game_end_date_time: datetime
    home_rotation_number: None
    away_rotation_number: None
    top_team_previous_game_id: None
    bottom_team_previous_game_id: None
    channel: None
    neutral_venue: None
    away_point_spread_payout: None
    home_point_spread_payout: None
    over_payout: None
    under_payout: None
    date_time_utc: datetime
    stadium: None
    periods: List[Periodlike]


def get_games(date : datetime) -> List[GamesByDatelike]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    domain = dotenv_values()["SPORTS_DATA_DOMAIN"]
    json = requests.get(
        f"{domain}/v3/cbb/scores/json/GamesByDate/{date.year}-{date.month}-{date.day}",
        params={
            "key" : dotenv_values()["SPORTS_DATA_KEY"]
        }
    ).json()
    return [GameByDate.parse_obj(g) for g in json]