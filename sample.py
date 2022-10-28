from gdg_model_builder import Model, private, session, spiodirect, universal, poll, secs, dow

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

@my_model.task(valid=dow(4))
async def say_hello(event = None):
    """Says hello

    Args:
        event (_type_, optional): _description_. Defaults to None.
    """
    print("Hello")

if __name__ == "__main__":
    my_model.start()
