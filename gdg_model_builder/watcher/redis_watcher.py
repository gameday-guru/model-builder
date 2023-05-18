from gdg_model_builder.watcher.watcher import Observer, Translator, S, E
from .watcher import Watcher
from gdg_model_builder.shape import Shape
from typing import Protocol, Generic, TypeVar, Callable, Awaitable
from asyncio import sleep
from asyncio.locks import Lock
import datetime
import math
import redis

class RedisWatcher(Watcher[S, E], Generic[S, E]):
    
    mean_time : int
    finds : int
    last_time : int
    sleep : float
    lock : Lock
    base : int
    store : redis.Redis
    
    def __init__(self, *, 
                 store : redis.Redis = redis.Redis(),
                 shape: type, event: type, observer: Callable[[], Awaitable], translator: Callable[[], Awaitable], id: str = "root") -> None:
        super().__init__(shape=shape, event=event, observer=observer, translator=translator, id=id)
        self.mean_time = 1
        self.finds = 0
        self.last_time = self.now()
        self.sleep = 1
        self.lock = Lock()
        self.base = 2
        self.store = store
        
    def _get_state_hash(self)->str:
        return f"{self.shape.identify()}:{self.id}"    
    
    async def neg_wait(self):
        await sleep(self.sleep/1000)
    
    async def pos_wait(self):
        
        # sleep however long the last step determined we should
        await self.neg_wait()
        
        # get the time from our internally represented clock
        t = self.now()
        
        # now we start mutating
        await self.lock.acquire()
        diff = t - self.last_time
        
        # we found another new value
        self.finds += 1
        
        # our mean time is now a weighted average
        # between the time it took for our most recent find
        # and the reset of our mean time
        self.mean_time = (
            self.mean_time *
            ((self.finds - 1)/self.finds)
        ) + (
            diff *
            ((1/self.finds))
        )
        
        # update the last time to this time
        self.last_time = t
        
        # update the sleep to a log of the mean time
        self.sleep = math.log(self.mean_time, self.base)
        # NOTE: given the above, you should be setting
        # your log base relatively low,
        # otherwise, you fill find yourself
        # checking your update condition a lot
        
        self.lock.release()
    
    async def tick(self) -> bool:
        res = await super().tick()
        if res:
            await self.pos_wait()
        else:
            await self.neg_wait()
        return res
    
    async def is_new(self, shape: S) -> bool:
        exists = self.store.sismember(
            self._get_state_hash(),
            shape.hash()
        )
        if not exists:
            return False
        self.store.sadd(
            self._get_state_hash(),
            shape.hash()
        )
        return True