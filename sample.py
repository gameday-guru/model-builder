from gdg_model_builder import Model, Shape

class Score(Shape):
    home : int
    away : int

my_model = Model()

current_score = my_model.state("current_score", Score)

async def get_score():
    score = await current_score.get()


if __name__ == "__main__":
    my_model.run()