from ast import Call
from typing import Dict, Protocol, TypeVar, Callable, ParamSpec, Awaitable
import cattrs
from model_builder.context.user.user import Userlike
from model_builder.context.context.context import Context
from model_builder.event.event import Event
from fastapi import FastAPI
import redis
import json
import concurrent.futures
import uvicorn

P = ParamSpec("P")
R = TypeVar("R")
RR = TypeVar("RR")
AC = Callable[P, Awaitable[R]]

CC = Callable[[*P, Context], Awaitable[R]]

CO = Callable[[Context], Awaitable[R]]

VO = Callable[[R, Context], Awaitable[RR]]

EO = Callable[[Event, Context], Awaitable[R]]

TC = Callable[[type[R]], RR]


class Modellike(Protocol):

    def method(self, func : AC)->AC:
        """Binds a method to the model.
        """
        pass

    def get(self, func : CO, key : str, *args, t : type[R])->TC:
        """Binds a retrieviable state to the model
        """
        pass

    def set(self, func : VO, key : str, *args,  value : R, t : type[R])->TC:
        """_summary_
        """
        pass

    def task(self, func : EO, e : type[Event])->EO:
        """_summary_
        """
        pass

    def emits(self, func : AC)->AC:
        pass

    async def emit(self, e : Event)->None:
        """_summary_
        """
        pass

    def acl(self, key : str, /)->str:
        """Creates an ACL at a given key.
        """
        pass

    def join_acl(self, *, key : str, user : Userlike)->str:
        pass

    async def start(self):
        pass

rc = redis.Redis(host='localhost', port=6379, db=0)

class Model(Modellike):

    app : FastAPI

    task_hashes : Dict[str, tuple[type, EO]] = {}

    task_listener_pool = concurrent.futures.ProcessPoolExecutor()

    app_op_pool = concurrent.futures.ProcessPoolExecutor()

    def __init__(self) -> None:
        super().__init__()
        self.app = FastAPI()


    def method(self, func : AC)->AC:
        """Binds a method to the model.
        """
        @self.app.post(func.__name__)
        async def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return func

    def get(self, func : CO, key : str, *args, t : type[R])->TC:
        """Binds a retrieviable state to the model
        """
        async def inner():
            obj = json.loads(rc.get(key))
            return func(cattrs.structure(obj, t))

        return inner

    def set(self, func : VO, key : str, *args, value : R, t : type[R])->TC:
        """_summary_
        """
        async def inner():
            obj = json.loads(rc.set(key, value))
            return func(cattrs.structure(obj, t))

        return inner

    def task(self, func : EO, e : type[Event])->EO:
        """_summary_
        """
        hash = e.get_hash()
        self.task_hashes[hash] = [e, EO]

        return func

    async def start(self):

        def run_app():
            uvicorn.run(self.app)

        def listen_tasks():

            md = {}
            for id in self.task_hashes:
                md[id] = 0

            while True:
                try:
                    for resp in rc.xread(md, count=1, block=50):
                        key, messages = resp[0]
                        t, c = self.task_hashes[key]
                        for m in messages:
                            c(cattrs.structure(m, t))
                            

                except ConnectionError as e:
                    print("ERROR REDIS CONNECTION: {}".format(e))

        self.task_listener_pool.submit(target=listen_tasks)

        self.app_op_pool.submit(target=run_app)

        

