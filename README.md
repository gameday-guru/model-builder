# gdg-model-builder
A toolkit for building a distributed services, developed at Gameday Guru for long-running sports gaming models.

## Install
We recommend using poetry.
```
poetry add gdg-model-builder
```
You can of course pip install as well.
```
pip install gdg-model-builder
```

## Architecture
`gdg-model-builder` is intended to be agnostic to its infrastructure. Provided the protocols are implemented your `Model Cluster` can be based on any form of data availablity and consensus. Currently, we provide implementations for redis out of the box.

## Features
`gdg-model-builder` introuduces several abstractions to ease in the creation of distributed services. It ties these into a distributed model runtime that supports retrodating out of the box.

As a general rule of thumb, the logic associated with any of these abstractions will not run redundantly within your cluster. One machine will take responsibility for performing a particular procedure. Machines can be working on many procedures at once.

Notably, however, `gdg-model-builder` provides an alpha `validated` decorator, which relies on a subset of nodes running the `validated` function. This is conceptually similar to how smart contracts work and is intended for use within trustless networks or for operations that necessitate consensus.

`validated` is not documented below as its use is discouraged for external users.

### `method`
A wrapper over FastAPI's `@app.post` which maintains usability of the decorated method.

```python
from gdg_model_builder import Model, Shape

my_model = Model()

class Score(Shape):
    home : int
    away : int

@my_model.method()
async def total_score(score : Score)->int:
    return score.home + score.away
```

### `state`
Manages persistent state and exposes API routes for said state. The `Collection` shape can be used to manage Pandas tables. 

```python
from gdg_model_builder import Model, Shape, Collection

# ...

class ScoresCollection(Collection[Score]):
    shape = Score

scores = my_model.state(ScoresCollection)
current_score = my_model.state(Score)

# can also be used as a decorator

@my_model.state
class ScoreCollectionAlternative(ScoresCollection):
    pass

async def add_one():
    scr = await scores.get()
    scr["1"] = Score(home=1, away=2)
    await scr.commit()
    
async def add_one_alternative():
    scr = await ScoreCollectionAlternative.get()
    scr["2"] = Score(home=2, away=3)
    await scr.commit()
```

### `task`
Listens for events and performs a task. Can be used in conjunction with `period` to create timed tasks.

```python
from gdg_model_builder import Model, Shape, Collection, Event

# ...

class TwoSecs(Event):
    pass

class RandomEvent(Event):
    pass

my_model.period(secs(2), TwoSecs) # EVERY TWO SECONDS

@my_model.task(TwoSecs)
async def handle_five_secs(event : TwoSecs)->None:
    print("Two seconds have passed!")
    if random.random() < 0.5:
        await my_model.emit(RandomEvent())
    
@my_model.task(RandomEvent)
async def handle_random_event(event : RandomEvent)->None:
    print("A random event was fired!")
```

### `watch`
Watches for new shapes. Useful for synchronizing with third-party data providers. By default, the polling strategy is managed by `gdg-model-builder`.

```python
@my_model.watch(IdScore)
async def poll_scores()->IdScore:
    print("Polling scores...")
    return IdScore(
        id=random.randint(0, 2), 
        home=random.randint(0, 2), 
        away=random.randint(0, 2)
    )
    
async def get_many_id_scores()->List[IdScore]:
    print("Polling many scores...")
    return [IdScore(
        id=random.randint(7, 9), 
        home=random.randint(7, 9), 
        away=random.randint(7, 9)
    ) for _ in range(4)]
    
@my_model.watch(IdScore)
async def poll_scores_bufferized()->List[IdScore]:
    return await debufferized(IdScore, await get_many_id_scores())

@my_model.task(IdScore)
async def handle_new_score(event : IdScore)->None:
    print("A new score was added!", event.id, event.home, event.away)
```
