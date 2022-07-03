# model-builder
The model-builder API for Gameday Guru.

## Install
```
pip install gdg-model-builder
```

## Sample Model
```python
from gdg_model_builder import session, Session, Model, Event

class MyEvent(Event):
    id = 2

# create a model
my_model = Model()

@my_model.method()
async def hello_world():
    return "Hello, world!"

@my_model.get("whose_house")
async def whose_house_universal():
    return "Our world."

@my_model.get("whose_house", session)
async def get_whose_world_user():
    return "your house."

@my_model.set("whose_house", session)
async def set_whose_world_user(val):
    return val

@my_model.task(MyEvent)
async def update_task():
   return do_thing()
```

## Model
The model is a contextual object that exposes all RPC methods, listens for events, and liases with other infrastructure.

## State
Persistent state (state maintained in the distributed store) can be set and retrieved via decorating handler logic with the `Model.get` and `Model.set` me methods.

```python
@my_model.method()
async def hello_world():
    return "Hello, world!"
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

@my_model.task(MyEvent)
async def update_task():
   return do_thing()
```
