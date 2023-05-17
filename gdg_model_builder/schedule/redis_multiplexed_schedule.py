from .multiplexed_schedule import MultiplexedSchedule, S
from .redis_schedule import RedisSchedule
from typing import Awaitable, Callable, Dict
from gdg_model_builder.shape import Shape
import redis
import asyncio

class RedisMultiplexedSchedule(MultiplexedSchedule):
    
    store : redis.Redis
    group : bytes
    consumer_id : bytes
    schedules : Dict[Shape, RedisSchedule]
    
    def __init__(
        self, *, 
        store = redis.Redis(), 
        group : bytes = b"1",
        consumer_id : bytes = b"1"
    ) -> None:
        
        super().__init__()
        
        self.store = store
        self.group = group
        self.consumer_id = consumer_id
        self.schedules = {}
    
    async def remove_handler(self, handler: Callable[[S], Awaitable[None]], Shape: type[S]):
        
        return await self.schedules[Shape].remove_handler(handler)
    
    async def add_handler(self, handler: Callable[[S], Awaitable[None]], Shape: type[S]):
        
        if Shape not in self.schedules:
            self.schedules[Shape] = RedisSchedule(
                store=self.store,
                group=self.group,
                consumer_id=self.consumer_id,
                Shape=Shape
            )
        
        return await self.schedules[Shape].add_handler(handler)
    
    async def emit(self, *, shape: Shape, force: bool = False) -> bool:
        
        if shape.__class__ not in self.schedules:
            self.schedules[shape.__class__] = RedisSchedule(
                store=self.store,
                group=self.group,
                consumer_id=self.consumer_id,
                Shape=shape.__class__
            )
        
        return await self.schedules[shape.__class__].emit(shape=shape, force=force)
    
    async def clean(self):
        
        await asyncio.gather(*[
            schedule.clean()
            for schedule in self.schedules.values()
        ])
    
    async def tick(self):
        
        await asyncio.gather(*[
            schedule.tick()
            for schedule in self.schedules.values()
        ])