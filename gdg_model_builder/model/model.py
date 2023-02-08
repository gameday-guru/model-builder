import asyncio
import concurrent.futures
from datetime import datetime
import json
import logging
import math
import os
import time
import uuid
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol, Sequence, TypeVar
from hashlib import sha256
from json import dumps
from dotenv import load_dotenv

import cattrs
from checksumdir import dirhash
import redis
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gdg_model_builder.context.bounds.bounds import Bound
from gdg_model_builder.context.context.context import Context, get_min_key
from gdg_model_builder.context.execution.execution import Execution
from gdg_model_builder.context.session.session import Session
from gdg_model_builder.context.user.user import User, Userlike
from gdg_model_builder.event.event import Event, exclusive, iproxy, pproxy
from gdg_model_builder.modifiers.state import private
import os
from gdg_model_builder.environment.environment import GDG_MODEL_HOSTNAME, GDG_REDIS_HOST, GDG_REDIS_PORT, GDG_BUMP_MODEL_START, bump_model_hostname

##################
### Type Vars ####
##################
P = TypeVar("P")
R = TypeVar("R")
RR = TypeVar("RR", bound=BaseModel) # base model return

AC = Callable[[P], Awaitable[R]]
CG = Callable[[Context], Awaitable[R]]
CO = Callable[[Context, R], Awaitable[R]]

EO = Callable[[Event, Context], Awaitable[R]]

LA = Callable[[float, Optional[float]], float]


# TODO: these need to be converted to tuple return types, one for the time of the event, one for the value used in cron serialization
def poll(now : float, last : float):
    return float(time.time())

def secs(count : int)->LA:
    def _secs(now : float, last : float):
        if last is None or (now - last)/1000 > count:
            return now
        return -1
    _secs.__name__ = f"_secs_{count}"
    return _secs

def mins(count : int)->LA:
    def _mins(now : float, last : float):
        if last is None or (now - last)/(1000 * 60) > count:
            return now
        return -1
    _mins.__name__ = f"_mins_{count}"
    return _mins

def hours(count : int)->LA:
    def _hours(now : float, last : float):
        if last is None or (now - last)/(1000 * 60 * 60) > count:
            return now
        return -1
    _hours.__name__ = f"_hours_{count}"
    return _hours

def days(count : int)->LA:
    def _days(now : float, last : float):
        if last is None or (now - last)/(1000 * 60 * 60 * 24) > count:
            return now
        return -1
    _days.__name__ = f"_days_{count}"
    return _days

def months(count : int)->LA:
    def _months(now : float, last : float):
        dt_now = datetime.fromtimestamp(now/1000)
        dt_last = datetime.fromtimestamp(last/1000)
        if last is None or (dt_now.month - dt_last.month) > count:
            return now
        return -1
    _months.__name__ = f"_months_{count}"
    return _months

def dow(which : int)->LA:
    def _dow(now : float, last : float):
        dt_now = datetime.fromtimestamp(now/1000)
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        last_epoch_days = now/(1000 * 60 * 60 * 24)
        if dt_now.toordinal() % 7 == which and (last is None or now_epoch_days != last_epoch_days):
            return now
        return -1
    _dow.__name__ = f"_months_{which}"
    return _dow

def date_once(*, which : str, format : str)->LA:
    def _date_once(now : float, last : float):
        date_str = datetime.strftime(which, format)
        now_epoch_days = now/(1000 * 60 * 60 * 24)
        now_str = datetime.fromtimestamp(now/1000).strftime(format)
        if last is None and date_str == now_str:
            return now
        return -1
    _date_once.__name__ = f"_months_{which}_{format}"
    return _date_once

# this is used to control stream starting and ignorance behavior
nonce = 'gamedaygurunoncenonotuseforanythingbutwhatisrecommendedherein'

class CronEvent(Event):
    """A Cron Event is an event with a time stamp
    """
    
    ts : float
    valid : LA
    
class Init(Event):
    """An Init event is an event that has init set to 1.
    """
    
    init : int = 1

class Modellike(Protocol):

    def method(self, func : AC)->AC:
        """Binds a method to the model.
        """
        pass

    def get(self, func : CO, key : str, *args, t : type[R])->Callable[[CO[R]], CG[R]]:
        """Binds a retrieviable state to the model
        """
        pass

    def set(self, func : CO, key : str, *args,  value : R, t : type[R])->Callable[[CO[R]], CO[R]]:
        """Decorates a setter, allowing it to perform state management
        """
        pass

    def task(self, func : EO, e : type[Event])->Callable[[EO], EO]:
        """Decorates a task, allowing it to be included in the distributed task loop.
        """
        pass

    def emit(self, e : Event)->None:
        """Emits an event.
        """
        pass

    def acl(self, key : str, /)->str:
        """Creates an ACL at a given key.
        """
        pass

    def join_acl(self, *, key : str, user : Userlike)->str:
        """Adds a user to an ACL.
        """
        pass

    async def start(self):
        """Starts the model
        """
        pass
    
    async def sim(self):
        """Simulates the model
        """
        pass
    
r = redis.Redis(host=GDG_REDIS_HOST, port=GDG_REDIS_PORT, db=0)

class PrivateMethodException(Exception):
    pass

class UninitializedEventException(Exception):
    pass

class ExclusiveEmitError(Exception):
    pass

class Model(Modellike):
    
    loop : asyncio.BaseEventLoop
    
    timefactor : int = 1
    retrodate : Optional[float] = None
    start_time : int = 0
    
    model_hostname : str = GDG_MODEL_HOSTNAME

    app : FastAPI
    
    store : redis.Redis

    event_handlers : Dict[str, List[tuple[type[Event], EO]]] = {}
    handler_loops : Dict[str, asyncio.BaseEventLoop] = {}
    cron_events : Dict[str, type[CronEvent]] = {}
    cron_logs : Dict[str, int] = {}

    cron_pool = concurrent.futures.ThreadPoolExecutor()
    task_listener_pool = concurrent.futures.ThreadPoolExecutor()
    handler_pool = concurrent.futures.ThreadPoolExecutor()
    server_pool = concurrent.futures.ThreadPoolExecutor()
    
    get_methods : Dict[Context, Dict[str, AC]] = {}
    set_methods : Dict[Context, Dict[str, AC]] = {}
    reified_methods : Dict[str, AC] = {}
    
    consumer_id : str
    
    cron_window : int
    
    converter = cattrs.Converter()
    
    history : bool = False


    def __init__(self, /, *, 
            store : redis.Redis = r, 
            cron_window : int = 15,
            history : bool = False,
            model_hostname : Optional[str] = None
    ) -> None:
        super().__init__()
        self.loop = asyncio.get_event_loop()
        
        if model_hostname:
            self.model_hostname = model_hostname
        else:
            # bump the model hostname if the environment requests it
            # TODO: this currently does not work and it may be better to make it CLI logic anyways
            bump_model_hostname()
            
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.store = store
        self.consumer_id = uuid.uuid1().hex
        self.cron_window = cron_window
        self.history = history


    def method(self, a : type[R], r : type[R])->Callable[[AC], AC]:
        """_summary_

        Args:
            a (type[R]): _description_
            r (type[R]): _description_

        Returns:
            Callable[[AC], AC]: _description_
        """
        def decorator(func : AC):
            
            @self.app.post(f"/method/{func.__name__}")
            async def inner(arg : a)->r:
                return await func(arg)
            return func
        return decorator

    def get(self, key : str, *args, t : type[R])->Callable[[CO[R]], CG[R]]:
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
                if self.history: 
                    obj = Model.parse_raw(self.store.lrange(get_min_key(bounds=args, key=self.get_inner_key(key), context=context), 0, 0)[0])
                    return await func(context, obj.data)
                else:
                    obj = Model.parse_raw(self.store.get(get_min_key(bounds=args, key=self.get_inner_key(key), context=context)))
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
           
    def get_inner_key(self, key : str):
        return f"{self.model_hostname}:{key}" 
    
    def register_handler_ready(self, event_hash : str)->bool:
        return self.store.set(f"ready:::{event_hash}", 1) 
   
    def handler_ready(self, event_hash : str)->bool:
       return self.store.exists(f"ready:::{event_hash}") > 0 

    def set(self, key : str, *args, t : type[R])->Callable[[CO[R]], CO[R]]:
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
                
                if self.history:
                    self.store.lpush(get_min_key(bounds=args, key=self.get_inner_key(key), context=context), Model(data=val).json())
                    return Model.parse_raw(self.store.lrange(get_min_key(bounds=args, key=self.get_inner_key(key), context=context), 0, 0)[0])
                else:
                    self.store.set(get_min_key(bounds=args, key=self.get_inner_key(key), context=context), Model(data=val).json())
                    return Model.parse_raw(self.store.get(get_min_key(bounds=args, key=self.get_inner_key(key), context=context)))
            
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
        
    def get_relative_event_hash(self, e : Event)->str:
        """Gets the event hash relative to this model.

        Args:
            e (Event): _description_

        Returns:
            str: _description_
        """
        if e.model_hostname is not None:
            return f"{e.model_hostname}:${e.get_event_hash()}"
        return f"{self.model_hostname}:${e.get_event_hash()}"
    
    def get_relative_event_instance_hash(self, e : Event)->str:
        """Gets the event instance hash relative to this model.

        Args:
            e (Event): _description_

        Returns:
            str: _description_
        """
        if e.model_hostname is not None:
            return f"{e.model_hostname}:${e.get_event_instance_hash()}"
        return f"{self.model_hostname}:${e.get_event_instance_hash()}"
    
    def get_event_lock_addr(self, e : Event)->str:
        return f"event:{self.get_relative_event_hash(e)}:{self.get_relative_event_instance_hash(e)}"
        
    def emit(self, e : Event):
        """Emits an event safely checking the lock while doing so.

        Args:
            e (Event): the event.

        Raises:
            UninitializedEventException: _description_
        """
        # intercept the emit based on exclusivity
        if e.particul == exclusive and e.model_hostname != self.model_hostname:
            print(e)
            raise ExclusiveEmitError(f"The event {e.__name__} is exclusive to {e.model_hostname}. You cannot emit it.")
        elif e.particul == iproxy and e.model_hostname != self.model_hostname:
            return
        elif e.particul == pproxy and e.model_hostname != self.model_hostname:
            return 
        
        event_hash = self.get_relative_event_hash(e)
        if event_hash not in self.event_handlers and (
            e.model_hostname is None
            or e.model_hostname == self.model_hostname
        ):
            raise UninitializedEventException()

        event_lock_addr = self.get_event_lock_addr(e)

        if e.nonce and self.store.exists(event_lock_addr):
            return
    
        self.store.set(event_lock_addr, self.consumer_id)
        
        lock_check = self.store.get(event_lock_addr).decode('utf-8')
        
        if(lock_check != self.consumer_id):
            # someone else hase the lock, someone else will dispatch
            return
    
        d = e.__dict__.copy()
        self.store.xadd(event_hash, d)

    def _task(self, e : type[Event] = None)->Callable[[EO], EO]:
        """Initializes a task for model.

        Args:
            func (EO): _description_
            e (type[Event]): _description_

        Returns:
            EO: _description_
        """
        if e.model_hostname is None:
            # tie it to this model if it isn't already associated somewhere
            e.model_hostname = self.model_hostname
        
        event_hash = self.get_relative_event_hash(e)
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
                
                # include in model
                model_hostname: Optional[str] = self.model_hostname
                __name__ = vfunc.__name__
                
                ts : float
                valid: LA = vfunc
                id : str = vfunc.__name__

                def __init__(self, *, ts : float) -> None:
                    super().__init__()
                    self.ts = ts
                    
            # add the cron class
            self.cron_events[self.get_relative_event_hash(Cron)] = Cron
            
            return self._task(Cron)
                    
    def _run_cron(self, status : int):
         while True:
            time.sleep(self.cron_window) 
            frontier = set(self.cron_events.keys())
            while len(frontier) > 0:
                for key in [*frontier]:
                    event = self.cron_events[key]
                    now = self.start_time + int((time.time() - self.start_time) * self.timefactor * 1000)
                    method_now = event.valid(now, self.cron_logs.get(key))
                    if method_now > -1:
                        cron_event = event(ts=method_now)
                        self.emit(cron_event)   
                        self.cron_logs[key] = method_now
                    frontier.remove(key)

          
    def run_retrodate(self, start : float):
        
        print("Retrodating...")
        flag = True
        timiter = start
        while flag: 
            time.sleep(0) # we want this to cycle through as fast as possible, but yield the procesor
            # we need to make sure this runs not just up to the time at which the loop began
            # but up to the actual time when the loop would finish
            frontier = set(self.cron_events.keys())
            while len(frontier) > 0:
                for key in [*frontier]:
                    event = self.cron_events[key]
                    method_now = event.valid(timiter * 1000, self.cron_logs.get(key))
                    if method_now > -1:
                        cron_event = event(ts=method_now)
                        ready = self.handler_ready(key)
                        if not ready:
                            continue
                        self.emit(cron_event)   
                        self.cron_logs[key] = method_now
                    frontier.remove(key)

            if timiter > time.time():
                flag = False
            timiter += 1
        print("Finished retrodating.")
    
    async def run_cron(self):
        
        if self.retrodate is not None: # retrodate the cron loop if possible
            await self.loop.run_in_executor(self.cron_pool, self.run_retrodate, self.retrodate)
        
        return await self.loop.run_in_executor(self.cron_pool, self._run_cron, 1)
            
    async def handle_task(self, routine : EO, event : Event, event_hash : str):
        await self.handler_loops[event_hash].create_task(
            routine(event)
        )
        
    async def read_task_stream(self, event_hash : str):
        """_summary_

        Args:
            event_hash (str): _description_
        """
        
        streams = dict()
        streams[event_hash] = '>'
        for resp in self.store.xreadgroup(self.model_hostname, self.consumer_id, streams, count=10, block=100):
            _, messages = resp
            
            tasks = []
            for id, message in messages:
                if nonce in [key.decode('utf-8') for key in message.keys()]:
                    # we want to ignore nonces
                    continue
                for EventType, routine in self.event_handlers[event_hash]:
                    d = {}
                    for key, value in message.items():
                        d[key.decode('utf-8')] = value.decode('utf-8')
                    tasks.append(self.handle_task(routine, EventType(**d), event_hash))
            await asyncio.gather(*tasks)

    def _listen_task(self, event_hash : str):
        """_summary_

        Args:
            event_hash (str): _description_
        """
        self.handler_loops[event_hash] = asyncio.new_event_loop()
        try: 
            self.store.xgroup_create(event_hash, self.model_hostname, mkstream=True)
        except Exception as e:
            pass
            # logging.exception(e)
            
        self.store.xgroup_createconsumer(event_hash, self.model_hostname, self.consumer_id)
        self.store.xadd(event_hash, {nonce : nonce})
        self.register_handler_ready(event_hash)
        
        while True:
            time.sleep(0)
            try:
                self.handler_loops[event_hash].run_until_complete(self.read_task_stream(event_hash))
            except Exception as e:
                logging.exception(e)
            
      
    
    async def listen_task(self, event_hash : str):
        """Listens to a task.

        Args:
            event_hash (str): _description_
        """
        await self.loop.run_in_executor(self.task_listener_pool, self._listen_task, event_hash)
    
    async def _listen_init(self):
        
        event_hash  = self.get_relative_event_hash(Init)
        init_key = self.get_init_key()

        try: 
            self.store.xgroup_create(event_hash, self.model_hostname, mkstream=True)
        except Exception as e:
            print(e)
        
        self.store.xgroup_createconsumer(event_hash, self.model_hostname, self.consumer_id)
        
        self.store.xadd(event_hash, {nonce : nonce})
        self.emit(Init(init=init_key))
        
        while not self.store.exists(init_key):
            time.sleep(1)
            streams = dict()
            streams[event_hash] = '>'
            for resp in self.store.xreadgroup(self.model_hostname, self.consumer_id, streams, count=10, block=1000):
                _, messages = resp
                for id, message in messages:
                    if nonce in [key.decode('utf-8') for key in message.keys()]:
                        # we want to ignore nonces
                        continue
                    for EventType, routine in self.event_handlers[event_hash]:
                        d = {}
                        for key, value in message.items():
                            d[key.decode('utf-8')] = value.decode('utf-8')
                        await routine(EventType(**d))
                        self.store.set(init_key, 1)
                        
        return True
          
    async def listen_init(self):
        
        Init.model_hostname = self.model_hostname
        event_hash  = self.get_relative_event_hash(Init)
        init_key = self.get_init_key()
        # hello next
    
        # make sure there's at least one event handler
        if Init.get_event_hash() not in self.event_handlers:
            @self.task(e=Init)
            async def handle_init(e):
                return
        return await self._listen_init()
        
        
    def get_instance_hash(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        cls = self.__class__
        obj_hash = sha256()
        obj_hash.update(cls.__name__.encode('utf-8'))
        obj_hash.update(str(self.model_hostname).encode('utf-8'))
        return obj_hash.digest().hex()
    
    def get_init_key(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.get_instance_hash()
    
    async def listen_tasks(self):
        """Listens for tasks
        """

        await self.listen_init()
     
        return await asyncio.gather(*[
            self.listen_task(id)
            for id in self.event_handlers
        ])
    
    def _run_server(self, status : int):
        """_summary_
        """
        uvicorn.run(self.app)
     
            
    async def run_server(self):
        """_summary_
        """
        return await self.loop.run_in_executor(self.server_pool, self._run_server, 1)
    
    async def _start(self):

        return await asyncio.gather(
            self.loop.create_task(self.listen_tasks()),
            self.loop.create_task(self.run_cron()),
            self.loop.create_task(self.run_server())
        )


    def start(self):
        
        self.loop.run_until_complete(self._start())

        

