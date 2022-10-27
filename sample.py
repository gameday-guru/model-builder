from model_builder import Model, private, session, spiodirect, universal

# create a model
my_model = Model()

@my_model.method()
async def hello_world():
    return "Hello, world!"

@my_model.get("whose_world", universal, private, t=str)
async def whose_world_global(context, val):
    return "everyone's world"

@my_model.get("whose_house", session, t=str)
async def get_whose_world_user(context, val):
    return await whose_world_global(context, val)

@my_model.set("whose_house", session, t=str)
async def set_whose_world_user(context, val):
    return val

@my_model.task(cron_str='46 * * * *')
async def say_hello():
    print("Hello")

if __name__ == "__main__":
    my_model.start()

"""
@my_model.task(136903)
async def update_task():
   return do_thing()
"""