from model_builder import session, Session, Model

# create a model
my_model = Model()

@my_model.method()
async def hello_world():
    return "Hello, world!"

@my_model.get("whose_world")
async def whose_world_global():
    return "Our world."

@my_model.get("whose_house", session)
async def get_whose_world_user():
    return "your house."

@my_model.set("whose_house", session)
async def set_whose_world_user(val):
    return val

@my_model.task(136903)
async def update_task():
   return do_thing()