from datetime import datetime
from typing import Any, Callable, Dict, List, Protocol, TypeVar, cast, Optional

import requests
from dotenv import dotenv_values
from pydantic import BaseModel
from json import dumps

class TeamSeasonStatslike(BaseModel):
    StatID : int
    TeamID : int
    SeasonType : int
    Season : int
    Name : str
    Team : Optional[str]
    Wins : Optional[int]
    Losses : Optional[int]
    ConferenceWins : Optional[int]
    ConferenceLosses : Optional[int]
    GlobalTeamID: int
    Possessions : float
    Updated : datetime
    Games : int
    FantasyPoints : float
    Minutes : int
    FieldGoalsMade : int
    FieldGoalsAttempted : int
    FieldGoalsPercentage : float
    EffectiveFieldGoalsPercentage : float
    TwoPointersMade : int
    TwoPointersAttempted : int
    TwoPointersPercentage : int
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
    Points: int
    TrueShootingAttempts : float
    TrueShootingPercentage : float
    PlayerEfficiencyRating : Optional[float]
    AssistsPercentage :  Optional[float]
    StealsPercentage :  Optional[float]
    BlocksPercentage :  Optional[float]
    TurnOversPercentage :  Optional[float]
    UsageRatePercentage :  Optional[float]
    FantasyPointsFanDuel :  Optional[float]
    FantasyPointsDraftKings :  Optional[float]
    FantasyPointsYahoo :  Optional[float]
    
class TeamSeasonStats(BaseModel):
    StatID : int
    TeamID : int
    SeasonType : int
    Season : int
    Name : str
    Team : Optional[str]
    Wins : Optional[int]
    Losses : Optional[int]
    ConferenceWins : Optional[int]
    ConferenceLosses : Optional[int]
    GlobalTeamID: int
    Possessions : float
    Updated : datetime
    Games : int
    FantasyPoints : float
    Minutes : int
    FieldGoalsMade : int
    FieldGoalsAttempted : int
    FieldGoalsPercentage : float
    EffectiveFieldGoalsPercentage : float
    TwoPointersMade : int
    TwoPointersAttempted : int
    TwoPointersPercentage : int
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
    Points: int
    TrueShootingAttempts : float
    TrueShootingPercentage : float
    PlayerEfficiencyRating : Optional[float]
    AssistsPercentage :  Optional[float]
    StealsPercentage :  Optional[float]
    BlocksPercentage :  Optional[float]
    TurnOversPercentage :  Optional[float]
    UsageRatePercentage :  Optional[float]
    FantasyPointsFanDuel :  Optional[float]
    FantasyPointsDraftKings :  Optional[float]
    FantasyPointsYahoo :  Optional[float]

def get_team_season_stats_by_date(date : datetime) -> List[TeamSeasonStats]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[TeamGameStatsByDatelike]: are the games by date.
    """
    domain = dotenv_values()["SPORTS_DATA_DOMAIN"]
    json = requests.get(
        f"{domain}/v3/cbb/scores/json/TeamSeasonStats/{date.year}",
        params={
            "key" : dotenv_values()["SPORTS_DATA_KEY"]
        }
    ).json()
    return [TeamSeasonStats.parse_obj(obj) for obj in json]