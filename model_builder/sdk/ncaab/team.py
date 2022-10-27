from typing import Optional, Protocol, Sequence

from pydantic import BaseModel
import requests
from dotenv import dotenv_values


class Stadiumlike(BaseModel):
    stadium_id: int
    active: bool
    name: str
    address: None
    city: str
    state: str
    zip: None
    country: None
    capacity: int
    geo_lat: float
    geo_long: float


class Teamlike(BaseModel):
    team_id: int
    key: str
    active: bool
    school: str
    name: str
    ap_rank: None
    wins: int
    losses: int
    conference_wins: int
    conference_losses: int
    global_team_id: int
    conference_id: int
    conference: str
    team_logo_url: str
    short_display_name: str
    stadium: Stadiumlike


class Stadium(BaseModel):
    stadium_id: int
    active: bool
    name: str
    address: None
    city: str
    state: str
    zip: None
    country: None
    capacity: int
    geo_lat: float
    geo_long: float


class Team(BaseModel):
    team_id: int
    key: str
    active: bool
    school: str
    name: str
    ap_rank: None
    wins: int
    losses: int
    conference_wins: int
    conference_losses: int
    global_team_id: int
    conference_id: int
    conference: str
    team_logo_url: str
    short_display_name: str
    stadium: Stadiumlike


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