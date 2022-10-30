from typing import Optional, Protocol, Sequence

from pydantic import BaseModel
import requests
from dotenv import dotenv_values


class Stadiumlike(BaseModel):
    StadiumID: int
    Active: bool
    Name: str
    Address: Optional[str]
    City: str
    State: str
    Zip: Optional[str]
    Country: Optional[str]
    Capacity: Optional[int]
    GeoLat: Optional[float]
    GeoLong: Optional[float]


class Teamlike(BaseModel):
    TeamID: int
    Key: str
    Active: bool
    School: str
    Name: str
    ApRank: Optional[int]
    Wins: Optional[int]
    Losses: Optional[int]
    ConferenceWins: Optional[int]
    ConferenceLosses: Optional[int]
    GlobalTeamID: int
    ConferenceID: Optional[int]
    Conference: Optional[str]
    TeamLogoUrl: str
    ShortDisplayName: str
    Stadium: Optional[Stadiumlike]



class Stadium(BaseModel):
    StadiumID: int
    Active: bool
    Name: str
    Address: Optional[str]
    City: str
    State: str
    Zip: Optional[str]
    Country: Optional[str]
    Capacity: Optional[int]
    GeoLat: Optional[float]
    GeoLong: Optional[float]


class Team(BaseModel):
    TeamID: int
    Key: str
    Active: bool
    School: str
    Name: str
    ApRank: Optional[int]
    Wins: Optional[int]
    Losses: Optional[int]
    ConferenceWins: Optional[int]
    ConferenceLosses: Optional[int]
    GlobalTeamID: int
    ConferenceID: Optional[int]
    Conference: Optional[str]
    TeamLogoUrl: str
    ShortDisplayName: str
    Stadium: Optional[Stadiumlike]


def get_teams()->Sequence[Teamlike]:
    """Gets all teams

    Returns:
        Sequence[Teamlike]: gets info about all teams
    """
    domain = dotenv_values()["SPORTS_DATA_DOMAIN"]
    return [
        Team.parse_obj(team)
        for team in requests.get(
        f"{domain}/v3/cbb/scores/json/teams",
        params={
            "key" : dotenv_values()["SPORTS_DATA_KEY"]
        }
    ).json()]

def get_team(id: str) -> Optional[Teamlike]:
    """Gets a team by id.

    Args:
        id (str): the id of the team.

    Returns:
        Optional[Teamlike]: _description_
    """
    for team in get_teams():
        if team.team_id == id:
            return team