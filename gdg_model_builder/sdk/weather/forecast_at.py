from typing import List, Optional

from pydantic import BaseModel, Field
from ...util.lru.lru import lru_cache_time

import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()


class Main(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    sea_level: int
    grnd_level: int
    humidity: int
    temp_kf: float


class WeatherItem(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class Clouds(BaseModel):
    all: int


class Wind(BaseModel):
    speed: float
    deg: int
    gust: float


class Rain(BaseModel):
    field_1h: float = Field(..., alias='1h')


class Sys(BaseModel):
    pod: str


class ForecastEntry(BaseModel):
    dt: int
    main: Main
    weather: List[WeatherItem]
    clouds: Clouds
    wind: Wind
    visibility: int
    pop: float
    rain: Optional[Rain] = None
    sys: Sys
    dt_txt: str


class Coord(BaseModel):
    lat: float
    lon: float


class City(BaseModel):
    id: int
    name: str
    coord: Coord
    country: str
    population: int
    timezone: int
    sunrise: int
    sunset: int


class Forecast(BaseModel):
    cod: str
    message: int
    cnt: int
    list: List[ForecastEntry]
    city: City
    
    
@lru_cache_time(300, 64)
def _get_forecast(*, lat : float, lng : float) -> Forecast:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    domain = os.getenv("OPEN_WEATHER_DATA_DOMAIN")
    key = os.getenv("OPEN_WEATHER_KEY")
    json = requests.get(
        f"{domain}/forecast/hourly?lat={lat}&lon={lng}&appid={key}",
    ).json()
    return Forecast.parse_obj(json)

def get_forecast(*, lat : float, lng : float) -> Forecast:
    """Gets games by date directly from sportsdataio

    Args:
        date (datetime): is the date in question.

    Returns:
        List[GameByDatelike]: are the games by date.
    """
    return _get_forecast(lat=lat, lng=lng)