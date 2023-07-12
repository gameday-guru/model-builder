from typing import Callable, Optional
from gdg_model_builder.clock import Predicate
from gdg_model_builder.state import State
from .model import Model, E, S, Task, M
from gdg_model_builder.schedule.redis_schedule import RedisSchedule
from gdg_model_builder.schedule.redis_multiplexed_schedule import RedisMultiplexedSchedule
from gdg_model_builder.clock.retro_clock import RetroClock
from fastapi import FastAPI
from gdg_model_builder.state.redis_state import RedisState
import uvicorn
import asyncio
import nest_asyncio
nest_asyncio.apply()
from gdg_model_builder.collection.collection import Collection, CollectionData
from gdg_model_builder.watcher import RedisWatcher, Observer, Translator, EventHandler
from gdg_model_builder.util import Symbol

class StandardModel(Model):
    
    id : str
    schedule : RedisMultiplexedSchedule
    clock : RetroClock
    app : FastAPI
    watchers : set[RedisWatcher]
    loop : asyncio.AbstractEventLoop
    latenecy : float
    
    def __init__(self) -> None:
        super().__init__()
        self.id = "test" # TODO: handle env id
        self.schedule = RedisMultiplexedSchedule()
        self.clock = RetroClock()
        self.app = FastAPI()
        self.loop = asyncio.get_event_loop()
        self.watchers = set()
        self.latenecy = 0.5
    
    def qualify_state_name(self, Shape : type[S], name : str)->str:
        return f"{self.id}::{Shape.identify().decode()}/{name}"
        
    def state(self, Shape: type[S], symbol : Optional[Symbol] = None) -> State[S]:
        
        if not symbol:
            symbol = Shape
        
        qname = self.qualify_state_name(Shape, symbol.__name__)
        this_state = RedisState[Shape](
            name=qname,
            typ=Shape
        )
        
        if issubclass(Shape, Collection):
            Sh : type[Collection] = Shape
            
            collection : Collection = Sh(name=qname)
            asyncio.run(this_state.set(collection))
            
            @self.app.post(f"/state/{qname}/{{id}}") 
            async def get_state(id : str)->Sh.shape:
                return collection[id]
            
            @self.app.post(f"/state/{qname}")
            async def get_state()->CollectionData:
                return CollectionData(
                    name=collection.name,
                    size=collection.size
                )
            
        else:
            
            @self.app.post(f"/state/{qname}")
            async def get_state()->Shape:
                return await this_state.get()
            
        return this_state
    
    async def emit(self, shape: E, *, force : bool = False) -> None:
        # TODO: I think we need to bind in the clock here.
        shape.overwrite_ts(self.clock.now()) # TODO: But, I'm not sure this is correct
        await self.schedule.emit(shape=shape, force=force)
    
    def task(self, Shape: type[E]) -> Callable[[Task[E]], Task[E]]:
        
        def innner(task : Task[E])->Task[E]:
            self.loop.run_until_complete(self.schedule.add_handler(task, Shape))
            return task
            
        return innner
    
    def watch(self, 
        Shape: type[S], 
        Event: Optional[type[E]] = None, 
        translator : Optional[Translator[S, E]] = None
    ) -> Callable[[Observer[S]], Observer[S]]:
        
        if Event is None:
            Event = Shape
        
        if translator is None:
            async def _translator(shape : S)->E:
                return shape
            translator = _translator
        
        def inner(observer : Observer[S])->Observer[S]:
            
            async def handle(event : E):
                await self.emit(event)
            
            # Use Redis Log mean watcher here
            watcher_runner = RedisWatcher(
                shape=Shape, event=Event,
                observer=observer, translator=translator,
            )
            watcher_runner.add_handler(handle)
            self.watchers.add(watcher_runner)
            
            async def force():
                _, res = await watcher_runner.tick(force=True)
                return res
            
            return force
        
        return inner
    
    def period(self, predicate: Predicate, Event : type[E]) -> None:
        
        async def handler(now : int):
            event = Event()
            event.overwrite_ts(now)
            # set the timestamp to the event
            await self.schedule.emit(shape=event)
            
        self.clock.add_task(
            predicate=predicate,
            task=handler
        )
    
    def method(self) -> Callable[[M], M]:
        
        def inner(method : M)->M:
            self.app.post(f"/method/{method.__name__}")(method)
            return method
        
        return inner
    
    async def run_clock(self):
        
        while True:
            await asyncio.sleep(self.latenecy)
            await self.clock.tick()
            
    async def run_watchers(self):
        
        while True:
            await asyncio.sleep(self.latenecy)
            for watcher in self.watchers:
                await watcher.tick()
                
    async def run_schedule(self):
        
        while True:
            await asyncio.sleep(self.latenecy)
            await self.schedule.tick()
            
    async def run_server(self):
        uvicorn.run(self.app)
            
    async def _run(self):
        await asyncio.gather(
            self.run_clock(),
            self.run_watchers(),
            self.run_schedule(),
            self.run_server()
        )
        
    def now(self) -> int:
        return self.clock.now()
        
    def run(self):
        asyncio.get_event_loop().run_until_complete(
            self._run()
        )     