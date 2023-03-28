from typing import Any, List, Optional, Dict
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from ...util.lru.lru import lru_cache_time
from datetime import datetime
load_dotenv()


from pydantic import BaseModel


class Stadium(BaseModel):
    StadiumID: int
    Active: bool
    Name: str
    City: str
    State: str
    Country: str
    Capacity: int
    Surface: str
    LeftField: int
    MidLeftField: int
    LeftCenterField: int
    MidLeftCenterField: int
    CenterField: int
    MidRightCenterField: int
    RightCenterField: int
    MidRightField: int
    RightField: int
    GeoLat: float
    GeoLong: float
    Altitude: int
    HomePlateDirection: int
    Type: str

    
@lru_cache_time(30000, 2)
def get_stadiums_table() -> Dict[int, Stadium]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    domain = os.getenv("SPORTS_DATA_DOMAIN")
    json = requests.get(
        f"{domain}/v3/mlb/scores/json/Stadiums",
        params={
            "key" : os.getenv("SPORTS_DATA_KEY")
        }
    ).json()
    
    stadiums_table = {}
    for g in json:
        stadium = Stadium.parse_obj(g)
        stadiums_table[stadium.StadiumID] = stadium
    return stadiums_table

def get_stadiums() -> List[Stadium]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    table : Dict[int, Stadium] = get_stadiums_table()
    return list(table.values())


def get_stadium(id : int) -> Optional[Stadium]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    table : Dict[int, Stadium] = get_stadiums_table()
    return table.get(id, None)