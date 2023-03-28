from typing import List, Optional

from pydantic import BaseModel, Field
from ...util.lru.lru import lru_cache_time

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from .forecast_at import ForecastEntry, get_forecast
from datetime import datetime


load_dotenv()


@lru_cache_time(60, 32)
def _get_weather_at(*, hour : int, day : int, month : int, year : int, lat : float, lng : float) -> ForecastEntry:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    forecast = get_forecast(lat=lat, lng=lng)
    for forecast_entry in forecast.list:
        date = datetime.fromtimestamp(forecast_entry.dt)
        if date.hour == hour and date.day == day and date.month == month and date.year == year:
            return forecast_entry
    return forecast.list[0]
    

def get_weather_at(*, date : datetime, lat : float, lng : float) -> ForecastEntry:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    return _get_weather_at(lat=lat, lng=lng, hour=date.hour, day=date.day, month=date.month, year=date.year)