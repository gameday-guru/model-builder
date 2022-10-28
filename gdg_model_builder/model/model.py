import asyncio
import concurrent.futures
from datetime import datetime
import json
import math
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Sequence, TypeVar
import pycron

import cattrs
import redis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from gdg_model_builder.context.bounds.bounds import Bound
from gdg_model_builder.context.context.context import Context, get_min_key
from gdg_model_builder.context.execution.execution import Execution
from gdg_model_builder.context.session.session import Session
from gdg_model_builder.context.user.user import User, Userlike
from gdg_model_builder.event.event import Event
from gdg_model_builder.modifiers.state import private

P = TypeVar("P")
R = TypeVar("R")
RR = TypeVar("RR", bound=BaseModel)

AC = Callable[[P], Awaitable[R]]
CO = Callable[[Context, R], Awaitable[R]]

EO = Callable[[Event, Context], Awaitable[R]]

LA = Callable[[int, Optional[int]], int]

def poll(now : int, last : int):
    return int(time.time())

def secs(count : int)->LA:
    def poll(now : int, last : int):
        if last is None or (now - last)/1000 > count:
            return int(time.time()/1000)
        return -1
    return poll

def mins(count : int)->LA:
    def poll(now : int, last : int):
        if last is None or (now - last)/(1000 * 60) > count:
            return int(time.time()/(1000 * 60))
        return -1
    return poll

def hours(count : int)->LA:
    def poll(now : int, last : int):
        if last is None or (now - last)/(1000 * 60 * 60) > count:
            return int(time.time()/(1000 * 60 * 60))
        return -1
    return poll

def days(count : int)->LA:
    def poll(now : int, last : int):
        if last is None or (now - last)/(1000 * 60 * 60 * 24) > count:
            return int(time.time()/(1000 * 60 * 60 * 24))
        return -1
    return poll

def months(count : int)->LA:
    def poll(now : int, last : int):
        dt_now = datetime.fromtimestamp(now/1000)
        dt_last = datetime.fromtimestamp(last/1000)
        if last is None or (dt_now.month - dt_last.month) > count:
            return dt_now.month
        return -1
    return poll

def dow(which : int)->LA:
    def poll(now : int, last : int):
        dt_now = datetime.fromtimestamp(now/1000)
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        last_epoch_days = now/(1000 * 60 * 60 * 24)
        if dt_now.toordinal() % 7 == which and (last is None or now_epoch_days != last_epoch_days):
            return now_epoch_days
        return -1
    return poll

def date_once(*, which : str, format : str)->LA:
    def poll(now : int, last : int):
        date_str = datetime.strftime(which, format)
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        now_str = datetime.fromtimestamp(now/1000).strftime(format)
        if last is None and date_str == now_str:
            return now_epoch_days
        return -1
    return poll
    
nonce = 'gamedaygurunoncenonotuseforanythingbutwhatisrecommendedherein'

class CronEvent(Event):
    
    windows : str
    valid : LA

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

    event_handlers : Dict[str, List[tuple[type[Event], EO]]] = {}
    cron_events : Dict[str, type[CronEvent]] = {}
    cron_logs : Dict[str, int] = {}

    cron_pool = concurrent.futures.ThreadPoolExecutor()
    task_listener_pool = concurrent.futures.ThreadPoolExecutor()
    server_pool = concurrent.futures.ThreadPoolExecutor()
    
    get_methods : Dict[Context, Dict[str, AC]] = {}
    set_methods : Dict[Context, Dict[str, AC]] = {}
    reified_methods : Dict[str, AC] = {}
    
    consumer_id : str
    
    cron_window : int
    
    converter = cattrs.Converter()


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
        event_hash = e.get_event_hash()
        event_instance_hash = e.get_event_instance_hash()
        if event_hash not in self.event_handlers:
            raise UninitializedEventException()
        
        event_lock_addr = f"event:{event_hash}:{event_instance_hash}"
        
        if e.nonce and self.store.exists(event_lock_addr):
            # someone has already posted this event
            return
        
        self.store.set(event_lock_addr, self.consumer_id)
        
        lock_check = self.store.get(event_lock_addr).decode('utf-8')
        
        if(lock_check != self.consumer_id):
            # someone else hase the lock, someone else will dispatch
            return

        self.store.xadd(event_hash, e.__dict__)

    def _task(self, e : type[Event] = None)->Callable[[EO], EO]:
        """Initializes a task for model.

        Args:
            func (EO): _description_
            e (type[Event]): _description_

        Returns:
            EO: _description_
        """
        event_hash = e.get_event_hash()
        if event_hash not in self.event_handlers:
            self.event_handlers[event_hash] = []
        
        def decorator(func : EO):
            # def inner(e : EventType):
                # self.store.xadd(event_hash, cattrs.unstructure(e,))
                # nothing
            self.event_handlers[event_hash].append([e, func])
            return func
        return decorator
    
    def task(self, e : type[Event] = None, valid : str = None)->Callable[[EO], EO]:
        
        if e is not None:
            return self._task(e)
        
        if e is None and valid is None:
            raise Exception()
        
        if e is None:
            vfunc = valid
            class Cron(CronEvent):
                windows : str
                valid: LA = vfunc
                
                def __init__(self, windows : int) -> None:
                    super().__init__()
                    self.windows = windows
                
            # add the cron class
            self.cron_events[Cron.get_event_hash()] = Cron
            
            return self._task(Cron)
                    
    def _run_cron(self, status : int):
         while True:
            time.sleep(self.cron_window) 
            for key, event in self.cron_events.items():
                now = int(time.time() * 1000)
                window = event.valid(now, self.cron_logs.get(key))
                if window > -1:
                    window = math.floor(time.time()/self.cron_window)
                    cron_event = event(window)
                    self.emit(cron_event)   
                    self.cron_logs[key] = now
        
    async def run_cron(self, loop : asyncio.BaseEventLoop):
        return await loop.run_in_executor(self.cron_pool, self._run_cron, 1)
    

    def handle_task(self, routine : EO, event : Event):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(routine(event))
        
    def read_task_stream(self, event_hash : str):
        
        for resp in self.store.xreadgroup(self.consumer_id, self.consumer_id, {
            event_hash : '>'
        }, count=10, block=50):
            _, messages = resp
            for id, message in messages:
                if nonce in message.keys():
                    # we want to ignore nonces
                    continue
                for EventType, routine in self.event_handlers[event_hash]:
                    self.handle_task(routine, EventType(message))

    def _listen_task(self, event_hash : str, loop : asyncio.BaseEventLoop):
        """_summary_

        Args:
            event_hash (str): _description_
        """
        self.store.xadd(event_hash, {nonce : nonce})
        self.store.xgroup_create(event_hash, self.consumer_id)
        self.store.xgroup_createconsumer(event_hash, self.consumer_id, self.consumer_id)
        
        while True:
            time.sleep(0)
            # may want to do some error handling here
            # self.store.xautoclaim(event_hash, self.consumer_id, self.consumer_id, min_idle_time=0, count=10)
            # claim the event for yourself

            try:
                self.read_task_stream(event_hash)
            except Exception as e:
                print(e)
            
      
    
    async def listen_task(self, event_hash : str, loop : asyncio.BaseEventLoop):
        """Listens to a task.

        Args:
            event_hash (str): _description_
        """
        
        return await loop.run_in_executor(self.task_listener_pool, self._listen_task, event_hash, loop)
          
    
    async def listen_tasks(self, loop : asyncio.BaseEventLoop):
        """Listens for tasks
        """

        return [
            await self.listen_task(id, loop)
            for id in self.event_handlers
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
        
        loop.run_until_complete(self._start(loop))

        

