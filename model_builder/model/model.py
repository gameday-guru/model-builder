import concurrent.futures
import json
import time
from tkinter import EventType
import uuid
from typing import Any, Awaitable, Callable, Dict, Protocol, Sequence, TypeVar

import cattrs
import redis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tomlkit import datetime

from model_builder.context.bounds.bounds import Bound
from model_builder.context.context.context import Context, get_min_key
from model_builder.context.execution.execution import Execution
from model_builder.context.session.session import Session
from model_builder.context.user.user import User, Userlike
from model_builder.event.event import Event
from model_builder.modifiers.state import private

P = TypeVar("P")
R = TypeVar("R")
RR = TypeVar("RR", bound=BaseModel)

AC = Callable[[P], Awaitable[R]]
CO = Callable[[Context, R], Awaitable[R]]

EO = Callable[[Event, Context], Awaitable[R]]

"""
class ModelBuilderCallable(Protocol, P):
    def __call__(self, *, context=Context, b: float) -> float:
        pass
"""

class Modellike(Protocol):

    def method(self, func : AC)->AC:
        """Binds a method to the model.
        """
        pass

    def get(self, func : CO, key : str, *args, t : type[R])->Callable[[CO], CO]:
        """Binds a retrieviable state to the model
        """
        pass

    def set(self, func : CO, key : str, *args,  value : R, t : type[R])->Callable[[CO], CO]:
        """_summary_
        """
        pass

    def task(self, func : EO, e : type[Event])->Callable[[EO], EO]:
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
    
r = redis.Redis(host='localhost', port=6379, db=0)

class PrivateMethodException(Exception):
    pass

class Model(Modellike):

    app : FastAPI
    
    store : redis.Redis

    event_hashes : Dict[str, tuple[type, EO]] = {}

    task_listener_pool = concurrent.futures.ProcessPoolExecutor()

    app_op_pool = concurrent.futures.ProcessPoolExecutor()
    
    get_methods : Dict[Context, Dict[str, AC]] = {}
    
    set_methods : Dict[Context, Dict[str, AC]] = {}
    
    reified_methods : Dict[str, AC] = {}
    
    consumer_id : str


    def __init__(self, /, *, store : redis.Redis = r) -> None:
        super().__init__()
        self.app = FastAPI()
        self.store = store
        self.consumer_id = uuid.uuid1()


    def method(self)->Callable[[AC], AC]:
        """Binds a method to the model.

        Args:
            func (AC): _description_

        Returns:
            AC: _description_
        """
        def decorator(func : AC):
            @self.app.post(func.__name__)
            async def inner(*args, **kwargs):
                return func(*args, **kwargs)
            return func
        return decorator

    def get(self, key : str, *args, t : type[R])->Callable[[CO], CO]:
        """Binds a get method to the model.

        Args:
            func (CO): _description_
            key (str): _description_
            t (type[R]): _description_

        Returns:
            TC: _description_
        """
        class Model(BaseModel):
            data : t
        
        def decorator(func : CO):

            async def inner(context : Context, *args):
                obj = Model.parse_raw(self.store.lrange(get_min_key(bounds=args, key=key, context=context), 0, 0)[0])
                return await func(context, obj.data)
            
            # register inner with get_methods map
            for arg in args:
                if arg in list(Bound):
                    # self.get_methods[arg][key] = inner
                    self.rpcify_get(key=key, bound=arg, getter=inner, t=Model, modifiers=args)

            return inner
        
        return decorator
    
    def rpcify_get(self, *, key : str, bound : Bound, getter : CO, t : type[RR], modifiers : Sequence[Any]):
        """_summary_

        Args:
            key (str): _description_
            bound (Bound): _description_
            getter (CO): _description_
        """
        if private in list(modifiers):
            return
        
        @self.app.post(f"/state/{key}/get/{{user}}/{{session}}/{bound.name}")
        async def get(user : str, session : str):
            res : t = await getter(Context(
                key = key,
                target=Bound[bound.name],
                user = User(
                    id = user,
                    connection_id=user
                ),
                session= Session(
                    id = session,
                    exp=time.time() * 1000 + 60000
                ),
                execution=Execution(
                    id=uuid.uuid4()
                )
            ))
            
            return JSONResponse(t(data=res).json())
            

    def set(self, key : str, *args, t : type[R])->Callable[[CO], CO]:
        """Binds a set method to the model.

        Args:
            func (CO): _description_
            key (str): _description_
            value (R): _description_
            t (type[R]): _description_

        Returns:
            TC: _description_
        """
        class Model(BaseModel):
            data : t
            
        def decorator(func : CO):
            async def inner(context : Context, value : R):
                val : R = await func(context, value)
                self.store.lpush(get_min_key(bounds=args, key=key, context=context), Model(data=val).json())
                return Model.parse_raw(self.store.lrange(get_min_key(bounds=args, key=key, context=context), 0, 0)[0])
            
            # register inner with get_methods map
            for arg in args:
                if arg in list(Bound):
                    self.rpcify_set(key=key, bound=arg, setter=inner, t=Model, modifiers=args)

            return inner
        
        return decorator
    
    def rpcify_set(self, *, key : str, bound : Bound, setter : CO, t : type[RR], modifiers : Sequence[Any]):
        """_summary_

        Args:
            key (str): _description_
            bound (Bound): _description_
            getter (CO): _description_
        """
        
        if private in list(modifiers):
            return
        
        @self.app.post(f"/state/{key}/set/{{user}}/{{session}}/{bound.name}")
        async def set(user : str, session : str, data : t):
            res : t = await setter(Context(
                key = key,
                target=Bound[bound.name],
                user = User(
                    id = user,
                    connection_id=user
                ),
                session= Session(
                    id = session,
                    exp=time.time() * 1000 + 60000
                ),
                execution=Execution(
                    id=uuid.uuid4()
                )
            ), data.data)
            return JSONResponse(res.json())

    def task(self, e : type[Event])->Callable[[EO], EO]:
        """Initializes a task for model.

        Args:
            func (EO): _description_
            e (type[Event]): _description_

        Returns:
            EO: _description_
        """
        event_hash = e.get_hash()
        self.event_hashes[event_hash] = [e, EO]
        def decorator(func : EO):
            def inner(e : EventType):
                self.store.xadd(hash, e)
                pass
                # nothing
            return func
        return decorator
    
    async def listen_task(self, task_id : str):
        
        self.store.xgroup_createconsumer(task_id, self.consumer_id, self.consumer_id)
        
        while True:
            # may want to do some error handling here
            for resp in self.store.xautoclaim(task_id, self.consumer_id, self.consumer_id, min_idle_time=0, count=10):
                key, messages = resp[0]
                task_type, coroutine = self.task_hashes[key]
                for message in messages:
                    coroutine(cattrs.structure(message, task_type))
          
    
    def listen_task(self, ):

        for id in self.event_hashes:
            


    def start(self):

        def run_app():
            uvicorn.run(self.app)
            
        run_app()

       

        # self.task_listener_pool.submit(listen_tasks)

        # self.app_op_pool.submit(run_app)

        

