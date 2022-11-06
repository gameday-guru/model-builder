from datetime import datetime
import json
from gdg_model_builder import Model, private, session, spiodirect, universal, Init, poll, secs, dow, Event

class FriendlyEvent(Event):
    note : str = "love"
    nonce : bool = False
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

# create a model
my_model = Model(cron_window=1)

@my_model.method()
async def hello_world():
    return "Hello, world!"

@my_model.get("whose_world", universal, private, t=str)
async def whose_world_global(context, val):
    return "everyone's world"

@my_model.get("whose_house", session, t=str)
async def get_whose_world_user(context, val):
    return val

@my_model.set("whose_house", session, t=str)
async def set_whose_world_user(context, val):
    return val

@my_model.task(valid=dow(5))
async def say_hello(event = None):
    """Says hello

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    print("Hello")


@my_model.task(valid=secs(5))
async def huzzah_hello(event = None):
    """Says huzzah

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    my_model.emit(FriendlyEvent(note="Hey!"))
    print("huzzah")
    
@my_model.task(e=FriendlyEvent)
async def huzzah_hello(event = None):
    """Says huzzah

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    print("Goodday!")
    
@my_model.task(e=Init)
async def first(event = None):
    """Says huzzah

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    print("First!")

if __name__ == "__main__":
    spiodirect.ncaab.get_team_season_stats_by_date(datetime.strptime("2022 12 01", "%Y %m %d"))
    my_model.start()
