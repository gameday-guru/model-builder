from datetime import datetime
from typing import Any, Callable, Dict, List, Protocol, TypeVar, cast, Optional
from ...util.lru.lru import lru_cache_time

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from json import dumps
import os

load_dotenv()

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

lru_cache_time(60, 32)
def _get_team_season_stats_by_date(*, year : int) -> List[TeamSeasonStats]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[TeamGameStatsByDatelike]: are the games by date.
    """
    domain = os.getenv("SPORTS_DATA_DOMAIN")
    json = requests.get(
        f"{domain}/v3/cbb/scores/json/TeamSeasonStats/{year}",
        params={
            "key" : os.getenv("SPORTS_DATA_KEY")
        }
    ).json()
    return [TeamSeasonStats.parse_obj(obj) for obj in json]

def get_team_season_stats_by_date(date : datetime) -> List[TeamSeasonStats]:
    
    return _get_team_season_stats_by_date(year=date.year)