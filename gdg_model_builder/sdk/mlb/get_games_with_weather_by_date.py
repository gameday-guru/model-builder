from typing import List, Optional

from pydantic import BaseModel, Field

import requests
from dotenv import load_dotenv
import os
from ..weather.forecast_at import ForecastEntry, get_forecast
from .weather_at_ballpark import get_weather_at_ballpark
from datetime import datetime
from .get_stadium import get_stadium
from .get_games_by_date import get_games_by_date, GameByDate
from pydantic import BaseModel

load_dotenv()

class GameWithWeatherByDate(BaseModel):
    forecast : ForecastEntry
    game : GameByDate
    

def get_games_with_weather_by_date(*, date : datetime ) -> ForecastEntry:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    games = get_games_by_date(date)
    games_with_weather = []
    for game in games:
        
        game_start = datetime.fromisoformat(game.DateTime)
        
        game_with_weather = GameWithWeatherByDate(
            game=game,
            forecast=get_weather_at_ballpark(
                date=game_start,
                stadium_id=game.StadiumID
            )
        )
        
        games_with_weather.append(game_with_weather)
        
    return games_with_weather