from typing import Any, List, Optional
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from ...util.lru.lru import lru_cache_time
from datetime import datetime
load_dotenv()


class GameByDate(BaseModel):
    GameID: int
    Season: int
    SeasonType: int
    Status: str
    Day: str
    DateTime: str
    AwayTeam: str
    HomeTeam: str
    AwayTeamID: int
    HomeTeamID: int
    RescheduledGameID: Any
    StadiumID: int
    Channel: Any
    Inning: Any
    InningHalf: Any
    AwayTeamRuns: Any
    HomeTeamRuns: Any
    AwayTeamHits: Any
    HomeTeamHits: Any
    AwayTeamErrors: Any
    HomeTeamErrors: Any
    WinningPitcherID: Any
    LosingPitcherID: Any
    SavingPitcherID: Any
    Attendance: Any
    AwayTeamProbablePitcherID: Any
    HomeTeamProbablePitcherID: Any
    Outs: Any
    Balls: Any
    Strikes: Any
    CurrentPitcherID: Any
    CurrentHitterID: Any
    AwayTeamStartingPitcherID: Any
    HomeTeamStartingPitcherID: Any
    CurrentPitchingTeamID: Any
    CurrentHittingTeamID: Any
    PointSpread: Any
    OverUnder: Any
    AwayTeamMoneyLine: Any
    HomeTeamMoneyLine: Any
    ForecastTempLow: Any
    ForecastTempHigh: Any
    ForecastDescription: Any
    ForecastWindChill: Any
    ForecastWindSpeed: Any
    ForecastWindDirection: Any
    RescheduledFromGameID: Any
    RunnerOnFirst: Any
    RunnerOnSecond: Any
    RunnerOnThird: Any
    AwayTeamStartingPitcher: Any
    HomeTeamStartingPitcher: Any
    CurrentPitcher: Any
    CurrentHitter: Any
    WinningPitcher: Any
    LosingPitcher: Any
    SavingPitcher: Any
    DueUpHitterID1: Any
    DueUpHitterID2: Any
    DueUpHitterID3: Any
    GlobalGameID: int
    GlobalAwayTeamID: int
    GlobalHomeTeamID: int
    PointSpreadAwayTeamMoneyLine: Any
    PointSpreadHomeTeamMoneyLine: Any
    LastPlay: Any
    IsClosed: bool
    Updated: str
    GameEndDateTime: Any
    HomeRotationNumber: Any
    AwayRotationNumber: Any
    NeutralVenue: bool
    InningDescription: Any
    OverPayout: Any
    UnderPayout: Any
    DateTimeUTC: str
    SeriesInfo: Any
    Innings: List

    
@lru_cache_time(60, 32)
def _get_games_by_date(*, day : int, month : int, year : int) -> List[GameByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    domain = os.getenv("SPORTS_DATA_DOMAIN")
    json = requests.get(
        f"{domain}/v3/mlb/scores/json/GamesByDate/{year}-{month}-{day}",
        params={
            "key" : os.getenv("SPORTS_DATA_KEY")
        }
    ).json()
    return [GameByDate.parse_obj(g) for g in json]

def get_games_by_date(date : datetime) -> List[GameByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    return _get_games_by_date(day=date.day, month=date.month, year=date.year)