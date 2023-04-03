from typing import List, Optional

from pydantic import BaseModel, Field

import requests
from dotenv import load_dotenv
import os
from ..weather.forecast_at import ForecastEntry, get_forecast
from ..weather.weather_at import get_weather_at
from datetime import datetime
from .get_stadium import get_stadium

load_dotenv()
    

def get_weather_at_ballpark(*, date : datetime, stadium_id : int ) -> ForecastEntry:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    stadium = get_stadium(id=stadium_id)
    return get_weather_at(date=date, lat=stadium.GeoLat, lng=stadium.GeoLong)