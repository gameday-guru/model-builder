from typing import Any, List, Optional
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from ...util.lru.lru import lru_cache_time
from datetime import datetime
load_dotenv()


class HomeStartingPitcher(BaseModel):
    PlayerID: int
    TeamID: int
    Team: str
    FirstName: str
    LastName: str
    BattingOrder: Any
    Position: str
    Starting: bool
    Confirmed: bool


class AwayStartingPitcher(BaseModel):
    PlayerID: int
    TeamID: int
    Team: str
    FirstName: str
    LastName: str
    BattingOrder: Any
    Position: str
    Starting: bool
    Confirmed: bool


class HomeBattingLineupItem(BaseModel):
    PlayerID: int
    TeamID: int
    Team: str
    FirstName: str
    LastName: str
    BattingOrder: int
    Position: str
    Starting: bool
    Confirmed: bool


class AwayBattingLineupItem(BaseModel):
    PlayerID: int
    TeamID: int
    Team: str
    FirstName: str
    LastName: str
    BattingOrder: int
    Position: str
    Starting: bool
    Confirmed: bool


class LineupsByDate(BaseModel):
    GameID: int
    Season: int
    SeasonType: int
    Day: str
    DateTime: str
    Status: str
    HomeTeamID: int
    HomeTeam: str
    AwayTeamID: int
    AwayTeam: str
    HomeStartingPitcher: HomeStartingPitcher
    AwayStartingPitcher: AwayStartingPitcher
    HomeBattingLineup: List[HomeBattingLineupItem]
    AwayBattingLineup: List[AwayBattingLineupItem]
    
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))
    
@lru_cache_time(60, 32)
def _get_lineups(*, day : int, month : int, year : int) -> List[LineupsByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    domain = os.getenv("SPORTS_DATA_DOMAIN")
    json = requests.get(
        f"{domain}/v3/mlb/scores/json/StartingLineupsByDate/{year}-{month}-{day}",
        params={
            "key" : os.getenv("SPORTS_DATA_KEY")
        }
    ).json()
    return [LineupsByDate.parse_obj(g) for g in json]

def get_lineups(date : datetime) -> List[LineupsByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    return _get_lineups(day=date.day, month=date.month, year=date.year)