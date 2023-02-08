from datetime import datetime
import json
from gdg_model_builder import Model, private, session, spiodirect, universal, Init, poll, secs, dow, days, Event
from pydantic import BaseModel
import uuid

class FriendlyEvent(Event):
    note : str = "love"
    nonce : bool = False
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
class Args(BaseModel): 
    a : int
    
class Returns(BaseModel):
    b : str
    
class ProjectionEntry(BaseModel):
    game_id : int
    home_team_id : int
    away_team_id : int
    home_team_score : float
    away_team_score : float
    
class ProjectionRequest(BaseModel):
    away_team_id : str
    home_team_id : str
    neutral : bool

# create a model
my_model = Model(cron_window=1)

class Thing(BaseModel):
    first : str

@my_model.method(a=ProjectionRequest, r=ProjectionEntry)
async def hello_world(a : ProjectionRequest)->ProjectionEntry:
    return  Returns(b="Hello world")

@my_model.get("whose_world", universal, private, t=str)
async def whose_world_global(context, val):
    return "everyone's world"

@my_model.get("whose_house", session, t=str)
async def get_whose_world_user(context, val):
    thing = await get_thing(context)
    return val

@my_model.get("thing", session, t=Thing)
async def get_thing(context, val):
    return val

@my_model.set("whose_house", session, t=str)
async def set_whose_world_user(context, val):
    return val

@my_model.task(valid=dow(6))
async def say_hello(event = None):
    """Says hello

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    print("Hello")


@my_model.task(e=Init)
async def what(event = None):
    print("Initializing...")

@my_model.task(valid=secs(1))
async def huzzah_hello(event = None):
    """Says huzzah

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    print("Hello", event.ts, datetime.fromtimestamp(float(event.ts)/1000))

if __name__ == "__main__":
    # my_model.retrodate = datetime.strptime("2023 1 20", "%Y %m %d").timestamp()
    # my_model.model_hostname = "sample"
    my_model.start()
