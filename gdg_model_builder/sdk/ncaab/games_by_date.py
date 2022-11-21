from datetime import datetime
from typing import Any, Callable, Dict, List, Protocol, TypeVar, cast, Optional
from .team import Stadiumlike

import requests
from dotenv import dotenv_values
from pydantic import BaseModel


class Periodlike(BaseModel):
    PeriodID: int
    GameID: int
    Number: int
    Name: str
    Type: str
    AwayScore: Optional[int]
    HomeScore: Optional[int]

class GameByDatelike(BaseModel):
    GameID: int
    Season: int
    SeasonType: int
    Status: str
    Day: datetime
    DateTime: Optional[datetime]
    AwayTeam: str
    HomeTeam: str
    AwayTeamID: int
    HomeTeamID: int
    AwayTeamScore: Optional[int]
    HomeTeamScore: Optional[int]
    Updated: datetime
    Period: Optional[str]
    TimeRemainingMinutes: Optional[int]
    TimeRemainingSeconds: Optional[int]
    PointSpread: Optional[float]
    OverUnder: Optional[float]
    AwayTeamMoneyLine: Optional[int]
    HomeTeamMoneyLine: Optional[int]
    GlobalGameID: int
    GlobalAwayTeamID: int
    GlobalHomeTeamID: int
    TournamentID: Optional[str]
    Bracket: Optional[str]
    Round: Optional[str]
    AwayTeamSeed: Optional[int]
    HomeTeamSeed: Optional[int]
    AwayTeamPreviousGameID: Optional[int]
    HomeTeamPreviousGameID: Optional[int]
    AwayTeamPreviousGlobalGameID: Optional[int]
    HomeTeamPreviousGloablGameID: Optional[int]
    TournamentDisplayOrder: Optional[int]
    TournamentDisplayOrderForHomeTeam: str
    IsClosed: bool
    GameEndDateTime: Optional[datetime]
    HomeRotationNumber: Optional[int]
    AwayRotationNumber: Optional[int]
    TopTeamPreviousGameID: Optional[str]
    BottomTeamPreviousGameID: Optional[str]
    Channel: Optional[str]
    NeutralVenue: Optional[bool]
    AwayPointSpreadPayout: Optional[str]
    HomePointSpreadPayout: Optional[str]
    OverPayout: Optional[str]
    UnderPayout: Optional[str]
    DateTimeUTC: Optional[datetime]
    Stadium: Optional[Stadiumlike]
    Periods: List[Periodlike]
    
class Period(BaseModel):
    PeriodID: int
    GameID: int
    Number: int
    Name: str
    Type: str
    AwayScore: Optional[int]
    HomeScore: Optional[int]

class GameByDate(BaseModel):
    GameID: int
    Season: int
    SeasonType: int
    Status: str
    Day: datetime
    DateTime: Optional[datetime]
    AwayTeam: str
    HomeTeam: str
    AwayTeamID: int
    HomeTeamID: int
    AwayTeamScore: Optional[int]
    HomeTeamScore: Optional[int]
    Updated: datetime
    Period: Optional[str]
    TimeRemainingMinutes: Optional[int]
    TimeRemainingSeconds: Optional[int]
    PointSpread: Optional[float]
    OverUnder: Optional[float]
    AwayTeamMoneyLine: Optional[int]
    HomeTeamMoneyLine: Optional[int]
    GlobalGameID: int
    GlobalAwayTeamID: int
    GlobalHomeTeamID: int
    TournamentID: Optional[str]
    Bracket: Optional[str]
    Round: Optional[str]
    AwayTeamSeed: Optional[int]
    HomeTeamSeed: Optional[int]
    AwayTeamPreviousGameID: Optional[int]
    HomeTeamPreviousGameID: Optional[int]
    AwayTeamPreviousGlobalGameID: Optional[int]
    HomeTeamPreviousGloablGameID: Optional[int]
    TournamentDisplayOrder: Optional[int]
    TournamentDisplayOrderForHomeTeam: str
    IsClosed: bool
    GameEndDateTime: Optional[datetime]
    HomeRotationNumber: Optional[int]
    AwayRotationNumber: Optional[int]
    TopTeamPreviousGameID: Optional[str]
    BottomTeamPreviousGameID: Optional[str]
    Channel: Optional[str]
    NeutralVenue: Optional[bool]
    AwayPointSpreadPayout: Optional[str]
    HomePointSpreadPayout: Optional[str]
    OverPayout: Optional[str]
    UnderPayout: Optional[str]
    DateTimeUTC: Optional[datetime]
    Stadium: Optional[Stadiumlike]
    Periods: List[Periodlike]


def get_games(date : datetime) -> List[GameByDatelike]:
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