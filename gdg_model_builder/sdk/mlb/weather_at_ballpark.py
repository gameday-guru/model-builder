from typing import List, Optional

from pydantic import BaseModel, Field
from ...util.lru.lru import lru_cache_time

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from ..weather.forecast_at import ForecastEntry, get_forecast
from ..weather.weather_at import get_weather_at
from datetime import datetime


load_dotenv()
    

def get_weather_at_ballpark(*, date : datetime, stadium_id : int ) -> ForecastEntry:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    return 