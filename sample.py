from gdg_model_builder import Model, Shape, Collection, Event
from gdg_model_builder.clock.predicates import secs
from gdg_model_builder.data import debufferized
import asyncio
import random
from typing import List

class Score(Shape):
    home : int
    away : int
    
class TwoSecs(Event):
    pass

class RandomEvent(Event):
    pass

class IdScore(Shape):
    id : int
    home : int
    away : int
    
class NewScore(Event):
    pass

my_model = Model()

class ScoresCollection(Collection[Score]):
    shape = Score

scores = my_model.state(ScoresCollection)
current_score = my_model.state(Score)

@my_model.state
class ScoreCollectionAlternative(ScoresCollection):
    pass

async def get_score():
    score = await current_score.get()

async def add_one():
    scr = await scores.get()
    scr["1"] = Score(home=1, away=2)
    await scr.commit()
    
async def add_one_alternative():
    scr = await ScoreCollectionAlternative.get()
    scr["2"] = Score(home=2, away=3)
    await scr.commit()

@my_model.method()
async def plus_plus(a : int)->int:
    return a + 1

@my_model.method()
async def total_score(score : Score)->int:
    return score.home + score.away

my_model.period(secs(2), TwoSecs)

@my_model.task(TwoSecs)
async def handle_five_secs(event : TwoSecs)->None:
    print("Two seconds have passed!")
    if random.random() < 0.5:
        await my_model.emit(RandomEvent())
    
@my_model.task(RandomEvent)
async def handle_random_event(event : RandomEvent)->None:
    print("A random event was fired!")
    
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

if __name__ == "__main__":
    asyncio.run(add_one())
    asyncio.run(add_one_alternative())
    my_model.run()