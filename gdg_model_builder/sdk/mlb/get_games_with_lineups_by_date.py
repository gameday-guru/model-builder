from typing import Any, List, Optional, Dict
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from ...util.lru.lru import lru_cache_time
from datetime import datetime
from .get_games_by_date import GameByDate, get_games_by_date
from .lineups_by_date import LineupsByDate, get_lineups
load_dotenv()


class GameWithLineupByDate(BaseModel):
    game : GameByDate
    lineups : LineupsByDate


def get_games_with_lineups_by_date(date : datetime) -> List[GameWithLineupByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    games = get_games_by_date(date)
    lineups = get_lineups(date)
    
    games_map = {}
    for game in games:
        games_map[game.GameID] = game
       
    games_with_lineups = [] 
    for lineup in lineups:
        if lineup.GameID in games_map:
            games_with_lineups.append(GameWithLineupByDate(
                game=games_map[lineup.GameID],
                lineups=lineup
            ))
    return games_with_lineups

@lru_cache_time(60, 32)
def get_games_with_lineups_by_table(date : datetime) -> Dict[int, GameWithLineupByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    games = get_games_by_date(date)
    lineups = get_lineups(date)
    
    games_map = {}
    for game in games:
        games_map[game.GameID] = game
       
    games_with_lineups = {}
    for lineup in lineups:
        if lineup.GameID in games_map:
            games_with_lineups[lineup.GameID] = (GameWithLineupByDate(
                game=games_map[lineup.GameID],
                lineups=lineup
            ))
    return games_with_lineups

def get_game_with_lineups_by_date(*, date : datetime, game_id : int) -> Optional[GameWithLineupByDate]:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    return get_games_with_lineups_by_table(date)[game_id]