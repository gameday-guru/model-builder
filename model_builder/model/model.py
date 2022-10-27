import asyncio
import concurrent.futures
import json
import math
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, Protocol, Sequence, TypeVar
import pycron

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

class UninitializedEventException(Exception):
    pass

class Model(Modellike):

    app : FastAPI
    
    store : redis.Redis

    event_hashes : Dict[str, tuple[type, EO]] = {}
    
    cron_events : Dict[str, Event] = {}

    cron_pool = concurrent.futures.ThreadPoolExecutor()
    task_listener_pool = concurrent.futures.ThreadPoolExecutor()
    server_pool = concurrent.futures.ThreadPoolExecutor()
    
    get_methods : Dict[Context, Dict[str, AC]] = {}
    
    set_methods : Dict[Context, Dict[str, AC]] = {}
    
    reified_methods : Dict[str, AC] = {}
    
    consumer_id : str
    
    cron_window : int


    def __init__(self, /, *, store : redis.Redis = r, cron_window : int = 15) -> None:
        super().__init__()
        self.app = FastAPI()
        self.store = store
        self.consumer_id = uuid.uuid1().hex
        self.cron_window = cron_window


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
                    id=uuid.uuid1().hex
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
                    id=uuid.uuid4().hex
                )
            ), data.data)
            return JSONResponse(res.json())
        
    def emit(self, e : Event):
        """Emits an event safely checking the lock while doing so.

        Args:
            e (Event): the event.

        Raises:
            UninitializedEventException: _description_
        """
        
        event_hash = e.__class__.get_hash()
        event_instance_hash = e.get_event_instance_hash()
        if e.__class__.get_hash() not in self.event_hashes:
            raise UninitializedEventException()
        
        event_lock_addr = f"event:{event_hash}:{event_instance_hash}"
        self.store.set(event_lock_addr, self.consumer_id)
        
        lock_check = self.store.get(event_lock_addr)
        
        if(lock_check != self.consumer_id):
            # someone else hase the lock, someone else will dispatch
            return
        
        self.store.xadd(event_hash, cattrs.unstructure(e, e.__class__))

    def _task(self, e : type[Event] = None)->Callable[[EO], EO]:
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
            # def inner(e : EventType):
                # self.store.xadd(event_hash, cattrs.unstructure(e,))
                # nothing
            return func
        return decorator
    
    def task(self, e : type[Event] = None, cron_str : str = None)->Callable[[EO], EO]:
        
        if e is not None:
            return self._task(e)
        
        if e is None and cron_str is None:
            raise Exception()
        
        if e is None:
            print(cron_str)
            cstr = cron_str
            class Cron(Event):
                fifteens : str
                cron_str : str = cstr
                
                def __init__(self, windows : int) -> None:
                    super().__init__()
                    self.windows = windows
                
            self.cron_events[Cron.cron_str] = Cron
            return self._task(Cron)
                    
    def _run_cron(self, status : int):
         while True:
            time.sleep(self.cron_window) 
            for cron_str in self.cron_events:
                if pycron.is_now(cron_str):  
                    window = math.floor(time.time()/self.cron_window)
                    cron_event = self.cron_events[cron_str](window)
                    self.emit(cron_event)   
        
    async def run_cron(self, loop : asyncio.BaseEventLoop):
        return await loop.run_in_executor(self.cron_pool, self._run_cron, 1)

    def _listen_task(self, event_hash : str):
        """_summary_

        Args:
            event_hash (str): _description_
        """
        self.store.xadd(event_hash, {"data" : "a"})
        self.store.xgroup_create(event_hash, self.consumer_id)
        self.store.xgroup_createconsumer(event_hash, self.consumer_id, self.consumer_id)
        
        while True:
            # may want to do some error handling here
            self.store.xautoclaim(event_hash, self.consumer_id, self.consumer_id, min_idle_time=0, count=10)
            # claim the event for yourself
            for resp in self.store.xreadgroup(self.consumer_id, self.consumer_id, {
                event_hash : 0
            }):
                _, messages = resp
                task_type, routine = self.event_hashes[event_hash]
                for message in messages:
                    routine(cattrs.structure(message, task_type))
    
    async def listen_task(self, event_hash : str, loop : asyncio.BaseEventLoop):
        """Listens to a task.

        Args:
            event_hash (str): _description_
        """
        
        return await loop.run_in_executor(self.task_listener_pool, self._listen_task, event_hash)
          
    
    async def listen_tasks(self, loop : asyncio.BaseEventLoop):
        """Listens for tasks
        """

        return [
            await self.listen_task(id, loop)
            for id in self.event_hashes
        ]
    
    def _run_server(self, status : int):
        """_summary_
        """
        uvicorn.run(self.app)
     
            
    async def run_server(self, loop : asyncio.BaseEventLoop):
        """_summary_
        """
        return await loop.run_in_executor(self.server_pool, self._run_server, 1)
    
    async def _start(self, loop : asyncio.BaseEventLoop = asyncio.get_event_loop()):
        return await asyncio.gather(
            self.listen_tasks(loop),
            self.run_cron(loop),
            self.run_server(loop)
        )


    def start(self, loop : asyncio.BaseEventLoop = asyncio.get_event_loop()):
        
        print(self.cron_events)
        
        loop.run_until_complete(self._start(loop))

        

