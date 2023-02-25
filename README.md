# model-builder
The model-builder API for Gameday Guru.

## Install
```
pip install gdg-model-builder
```

## Sample Model
```python
from gdg_model_builder import session, universal, Model, Event

class MyEvent(Event):
    id = 2

# create a model
my_model = Model()

@my_model.method()
async def hello_world(t=str):
    return "Hello, world!"

@my_model.get("whose_house", universal)
async def set_whose_house_universal():
    return "Our world."

@my_model.get("whose_house", session)
async def get_whose_world_session():
    return "your house."

@my_model.set("whose_house", session)
async def set_whose_world_user(val):
    return val

@my_model.task(MyEvent)
async def update_task():
   return do_thing()
```

## Model
The model is a contextual object that exposes all RPC methods, listens for events, and liases with infrastructure.

## State
Persistent state (state maintained in the distributed store) can be set and retrieved via decorating handler logic with the `Model.get` and `Model.set` me methods.

```python
@my_model.get("whose_house", t=House)
async def get_whose_house_universal():
    return "Our world."
```

State getters will receive a value that is serialized based on a type object in the decorator.
```python
@my_model.get("whose_house", t=House)
async def get_whose_house_universal(h : House):
    # perhaps modify house and return it
    return h
    
async def do_get_thing():
    house = await my_model.get_state("whose_house", universal) # by model
    house = await get_whose_house_universal() # by implementation
```

State setters will receive a value that is serialized based on a type object in the decorator.
```python
@my_model.set("whose_house", session, t=House)
async def set_whose_world_session(val):
    return val
    
async def do_set_thing():
    house = await my_model.set_state("whose_house", House(), session) # by model, invokes the state setter above
    house = await set_whose_world_session(House()) # by implementation
```


### State Bounds
State can be bound to one of the `execution`, `session`, `user`, or `universal` contexts, meaning it will carry a unique value in this context if one is provided. 

```python
@my_model.get("whose_house", session)
async def get_whose_world_user():
    return "your house."

@my_model.set("whose_house", session)
async def set_whose_world_user(val):
    return val
```

The classes `Execution`, `Session`, `User`, and `Universal` can be used in place of the lowercase enums.

```python
from gdg_model_builder import Session

@my_model.get("whose_house", Session)
async def get_whose_world_user():
    return "your house."

@my_model.set("whose_house", Session)
async def set_whose_world_user(val):
    return val
```

## Tasks
Callbacks can be specified for events. Many are provided by the GDG SDK. But, you may also define your own.

Event hash collisions are avoided by the model-builder backend. You do not have to worry about your Events colliding with those of other models.

```python
class MyEvent(Event):
    id = 2

@my_model.task(e=MyEvent)
async def update_task(e : MyEvent):
   return do_thing()
```

## Watchers
Watchers can be used to construct simple events based on the difference in a collection. 

```python
# create an empty event
class WatchedEvent(Event):
    pass

@my_model.watch(e=WatchedEvent)
async def watch_names():
    return await get_names_from_db()
```

By default, the above will populate an `eid : bytes` field with a naive hash of the each element in the iterable returned by `get_names_from_db()`. You could pair this with a task as follows.

```python
# create an empty event
class MyWatchedEvent(Event):
    pass

@my_model.watch(e=MyWatchedEvent)
async def watch_names():
    return await get_names_from_db()

@my_model.task(e=MyWatchedEvent)
async def alert_new_member(e : MyWatchedEvent):
    await send_alert_using_naive_hash(e.eid)
```

Maybe we could do something like this...
```python
@my_model.watch_task(e=MyWatchedEvent, watcher=get_names_from_db)
async def watch_names():
    await send_alert_using_naive_hash(e.eid)
```

In most cases, however, you will want to define the hashing behavior, or the manner in which the event is created.

Using the `hash` kwarg, you will simply change the procedure for producing the `eid : bytes` value.

```python
# create an empty event
class MyWatchedEvent(Event):
    pass

@my_model.watch(e=MyWatchedEvent, hash=bytes_of_str)
async def watch_names():
    return await get_names_from_db()

@my_model.task(e=MyWatchedEvent)
async def alert_new_member(e : MyWatchedEvent):
    await send_alert_using_str(str(e.eid)) # now this can be interepretted as a string
```

Using the `make` kwarg, you will change the procedure for making the event itself.

```python
# create an event
class MyWatchedEvent(WatchedEvent[str]):
    name : str

    @classmethod
    def from_source(cls, source : str):
        return MyWatchedEvent(
            name=source
        )

@my_model.watch(e=MyWatchedEvent)
async def watch_names():
    return await get_names_from_db()

@my_model.task(e=MyWatchedEvent)
async def alert_new_member(e : MyWatchedEvent):
    await send_alert_using_str(e.name) # now this can be interepretted as a string
```

You can do the same by typing your event and overriding the `from_source` method.

```python
# create an event
class MyWatchedEvent(Event):
    name : str

@my_model.watch(e=MyWatchedEvent, make=event_with_name)
async def watch_names():
    return await get_names_from_db()

@my_model.task(e=MyWatchedEvent)
async def alert_new_member(e : MyWatchedEvent):
    await send_alert_using_str(e.name) # now this can be interepretted as a string
```

## Default state handlers
Sometimes there is no need clean the value before providing it to the client. For these usecases, you can simply `pass` or `return None` from your state management methods.

```python
class GameScore(BaseModel):
    home : int
    away : int

@my_model.get("game_score", t=GameScore)
async def get_game_score(val):
    pass
    # return None

```

## Collection types
You will often find it best to store state as a collection. For this purpose, we recommend the using on of our collection types. Most commonly you should resort to `Table`.

### Table
```python
class GameScore(BaseModel):
    id : str
    home : int
    away : int

@my_model.get("game_scores", t=Table[GameScore.id, GameScore])
async def get_game_scores(val):
    pass
```

Tables can be worked with in a variety of ways, they are foremost a dictionary with keys pointing to values in the collection.

```python
game_scores = await get_game_scores()
game_scores["1"] = GameScore(
    # ...
)
```

They also colocate a dataframe at the `.frame` member. This dataframe is derived from `polars`.
```python
avg = game_scores.frame.select("home").avg()
```

### Staging
You can work with `Table` data in a safe staging environment referred to as the draft. You modify read and write behavior as follows.

```python
class ReadMode(Enum):
    READ_THROUGH = 0 # reads through to the underlying database
    READ_LATENT = 1 # reads through if a value in the draft is too old
    READ_DRAFT = 2 # reads from the draft if a value exists, otherwise DB
    READ_DRAFT_ONLY = 3 # reads only from the draft

class WriteMode(Enum):
    WRITE_THROUGH = 0 # writes through to the underlying database
    WRITE_DRAFT = 1 # writes to the draft
    
class DeleteMode(Enum):
    DELETE_THROUGH = 0 # deletes through to the underlying database
    DELETE_DRAFT = 1 # deletes from the draft
    
class EnforcementMode(Enum):
    ENFORCE_AUTO = 0 # will automatically commit the state when the method ends
    ENFORCE_SIGNED = 1 # will commit up to the last "signed" changes
    ENFORCE_MANUAL = 2 # requires developer to commit the changes
```

You can set the disposition of the Table using the `.stage` method. 
```python
game_scores = await get_game_scores() 
# by default, the disposition will be:
# READ_LATENT
# WRITE_DRAFT
# DELETE_DRAFT
# ENFORCE_AUTO
```

If you wanted to require your own commit management, you could then stage as folows.

```python
game_scores.stage(enforce=ENFORCE_MANUAL)
```

You could then decide whether to commit or uncommit

```python
if is_true():
    game_scores.commit()
else: 
    game_scores.uncommit()
```

However, if the above is not set to MANUAL, any of the `@my_model` decorated methods will automatically handle committing the changes for you. It's as if there were a `game_scores.commit()` at the end of every function.

Signed committing behavior is useful in a multistage pipeline. The basic concept is that you can add to a list of signees. The commit will only take place automatically if all signees have signed their participation in the pipeline

```python
game_scores.add_signee(signee)
games_scores.stage(enforce=ENFORCE_SIGNED)
```

## Non-string keys
TODO

## Sports Helpers 
TODO
