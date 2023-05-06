from typing import Callable
from gdg_model_builder.clock import Predicate
from gdg_model_builder.model.model import Watcher
from gdg_model_builder.state import State
from .model import Model, E, S, Task, M
from gdg_model_builder.schedule.redis_schedule import RedisSchedule
from gdg_model_builder.clock.retro_clock import RetroClock
from fastapi import FastAPI

class StandardModel(Model):
    
    schedule : RedisSchedule
    clock : RetroClock
    app : FastAPI
    
    async def state(self, name: str, Shape: type[S]) -> State[S]:
        
        # TODO: use FastAPI + Redis state here
        return super().state(name, Shape)
    
    async def emit(self, shape: E, *, force : bool = False) -> None:
        await self.schedule.emit(shape, force=force)
    
    async def task(self, Shape: type[E]) -> Callable[[Task[E]], Task[E]]:
        
        async def innner(task : Task[E])->Task[E]:
            
            await self.schedule.add_handler(task, Shape)
            return task
            
        return innner
    
    async def watch(self, Shape: type[S], Event: type[E]) -> Callable[[Watcher[S]], Watcher[S]]:
        
        # Use Redis Log mean watcher here
        return super().watch(Shape, Event)
    
    async def period(self, predicate: Predicate, Event : E) -> None:
        
        async def handler(now : int):
            event = Event()
            event.overwrite_ts(now)
            # set the timestamp to the event
            self.schedule.emit(event)
            
        self.clock.add_task(
            predicate=predicate,
            task=handler
        )
    
    async def method(self) -> Callable[[M], M]:
        
        # TODO: use app here
        return super().method()
    
    async def run_clock(self):
        
        while True:
            await self.clock.tick()
                