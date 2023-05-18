from gdg_model_builder import Model, Shape, Collection
import asyncio

class Score(Shape):
    home : int
    away : int

my_model = Model()

class ScoresCollection(Collection[Score]):
    shape = Score

scores = my_model.state("scores", ScoresCollection)
current_score = my_model.state("current_score", Score)

async def get_score():
    score = await current_score.get()

async def add_one():
    scr = await scores.get()
    scr["1"] = Score(home=1, away=2)
    await scr.commit()

if __name__ == "__main__":
    asyncio.run(add_one())
    my_model.run()