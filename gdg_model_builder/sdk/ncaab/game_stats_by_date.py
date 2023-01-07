from datetime import datetime
from typing import Any, Callable, Dict, List, Protocol, TypeVar, cast, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from json import dumps
import os

load_dotenv()

class TeamGameStatsByDatelike(BaseModel):
    StatID : int
    TeamID : int
    SeasonType : int
    Season : int
    Name : str
    Team : str
    Wins : Optional[int]
    Losses : Optional[int]
    ConferenceWins : Optional[int]
    ConferenceLosses : Optional[int]
    GlobalTeamID : Optional[int]
    Possessions : Optional[int]
    GameID : int
    OpponentID : int
    Opponent : str
    Day : Optional[datetime]
    DateTime : Optional[datetime]
    HomeOrAway : str
    IsGameOver : bool
    GlobalGameID : int
    GlobalOpponentID : int
    Updated : Optional[datetime]
    Games : int
    FantasyPoints : Optional[float]
    Minutes : Optional[int]
    FieldGoalsMade : int
    FieldGoalsAttempted : int
    FieldGoalsPercentage : int
    EffectiveFieldGoalsPercentage : float
    TwoPointersMade : int
    TwoPointersAttempted : int
    TwoPointersPercentage : float
    ThreePointersMade : int
    ThreePointersAttempted : int
    ThreePointersPercentage : float
    FreeThrowsMade : int
    FreeThrowsAttempted : int
    FreeThrowsPercentage : float
    OffensiveRebounds : int
    DefensiveRebounds : int
    Rebounds : int
    OffensiveReboundsPercentage : Optional[float]
    DefensiveReboundsPercentage : Optional[float]
    TotalReboundsPercentage : Optional[float]
    Assists : int
    Steals : int
    BlockedShots : int
    Turnovers : int
    PersonalFouls : int
    Points : Optional[int]
    TrueShootingAttempts : float
    TrueShootingPercentage : float
    PlayerEfficiencyRating : Optional[float]
    AssistsPercentage : Optional[float]
    StealsPercentage : Optional[float]
    BlocksPercentage : Optional[float]
    TurnOversPercentage : Optional[float]
    UsageRatePercentage : Optional[float]
    FantasyPointsFanDuel : Optional[float]
    FantasyPointsDraftKings : Optional[float]
    FantasyPointsYahoo : Optional[float]

class TeamGameStatsByDate(BaseModel):
    StatID : int
    TeamID : int
    SeasonType : int
    Season : int
    Name : str
    Team : str
    Wins : Optional[int]
    Losses : Optional[int]
    ConferenceWins : Optional[int]
    ConferenceLosses : Optional[int]
    GlobalTeamID : Optional[int]
    Possessions : Optional[int]
    GameID : int
    OpponentID : int
    Opponent : str
    Day : Optional[datetime]
    DateTime : Optional[datetime]
    HomeOrAway : str
    IsGameOver : bool
    GlobalGameID : int
    GlobalOpponentID : int
    Updated : Optional[datetime]
    Games : int
    FantasyPoints : Optional[float]
    Minutes : Optional[int]
    FieldGoalsMade : int
    FieldGoalsAttempted : int
    FieldGoalsPercentage : int
    EffectiveFieldGoalsPercentage : float
    TwoPointersMade : int
    TwoPointersAttempted : int
    TwoPointersPercentage : float
    ThreePointersMade : int
    ThreePointersAttempted : int
    ThreePointersPercentage : float
    FreeThrowsMade : int
    FreeThrowsAttempted : int
    FreeThrowsPercentage : float
    OffensiveRebounds : int
    DefensiveRebounds : int
    Rebounds : int
    OffensiveReboundsPercentage : Optional[float]
    DefensiveReboundsPercentage : Optional[float]
    TotalReboundsPercentage : Optional[float]
    Assists : int
    Steals : int
    BlockedShots : int
    Turnovers : int
    PersonalFouls : int
    Points : Optional[int]
    TrueShootingAttempts : float
    TrueShootingPercentage : float
    PlayerEfficiencyRating : Optional[float]
    AssistsPercentage : Optional[float]
    StealsPercentage : Optional[float]
    BlocksPercentage : Optional[float]
    TurnOversPercentage : Optional[float]
    UsageRatePercentage : Optional[float]
    FantasyPointsFanDuel : Optional[float]
    FantasyPointsDraftKings : Optional[float]
    FantasyPointsYahoo : Optional[float]


def get_game_stats_by_date(date : datetime) -> List[TeamGameStatsByDatelike]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[TeamGameStatsByDatelike]: are the games by date.
    """
    domain = os.getenv("SPORTS_DATA_DOMAIN")
    json = requests.get(
        f"{domain}/v3/cbb/scores/json/TeamGameStatsByDate/{date.year}-{date.month}-{date.day}",
        params={
            "key" : os.getenv("SPORTS_DATA_KEY")
        }
    ).json()
    return [TeamGameStatsByDate.parse_obj(entry) for entry in json]