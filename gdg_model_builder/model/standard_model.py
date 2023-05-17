from typing import Callable
from gdg_model_builder.clock import Predicate
from gdg_model_builder.model.model import Watcher
from gdg_model_builder.state import State
from .model import Model, E, S, Task, M
from gdg_model_builder.schedule.redis_schedule import RedisSchedule
from gdg_model_builder.schedule.redis_multiplexed_schedule import RedisMultiplexedSchedule
from gdg_model_builder.clock.retro_clock import RetroClock
from fastapi import FastAPI
from gdg_model_builder.state.redis_state import RedisState

class StandardModel(Model):
    
    id : str
    schedule : RedisMultiplexedSchedule
    clock : RetroClock
    app : FastAPI
    
    def qualify_state_name(self, name : str, Shape : type[S])->str:
        return f"{self.id}.{Shape.identify().decode()}:{name}"
        
    
    def state(self, name: str, Shape: type[S]) -> State[S]:
        
        # TODO: use FastAPI + Redis state here
        qname = self.qualify_state_name(name, Shape)
        this_state = RedisState[Shape](
            name=name,
            Shape=Shape
        )
        
        @self.app.get(f"state/{qname}")
        async def get_state()->Shape:
            return await this_state.get()
            
        return this_state
    
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
    
    async def period(self, predicate: Predicate, Event : type[E]) -> None:
        
        async def handler(now : int):
            event = Event()
            event.overwrite_ts(now)
            # set the timestamp to the event
            await self.schedule.emit(event)
            
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
                