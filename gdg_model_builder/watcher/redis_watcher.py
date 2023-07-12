from gdg_model_builder.watcher.watcher import Observer, Translator, S, E
from .watcher import Watcher
from gdg_model_builder.shape import Shape
from typing import Protocol, Generic, TypeVar, Callable, Awaitable, Tuple
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
    store : redis.Redis
    power : float
    
    def __init__(self, *, 
                 store : redis.Redis = redis.Redis(),
                 shape: type, event: type, observer: Callable[[], Awaitable], translator: Callable[[], Awaitable], id: str = "root") -> None:
        super().__init__(shape=shape, event=event, observer=observer, translator=translator, id=id)
        self.mean_time = 1000
        self.power = 2/3
        self._update_sleep()
        self.finds = 0
        self.last_time = self.now()
        self.lock = Lock()
        self.store = store
        
    def _update_sleep(self):
        power_product = self.mean_time ** self.power
        self.sleep = power_product * math.log2(self.mean_time) - power_product
        
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
        
        # print(self.mean_time, self.sleep, diff)
        
        # we found another new value
        self.finds += 1
        
        # our mean time is now a weighted average
        # between the time it took for our most recent find
        # and the reset of our mean time
        self.mean_time = int((
            self.mean_time *
            ((self.finds - 1)/self.finds)
        ) + (
            diff *
            ((1/self.finds))
        ))
        
        # update the last time to this time
        self.last_time = t
        
        # update the sleep to a log of the mean time
        self._update_sleep()
        # NOTE: given the above, you should be setting
        # your log base relatively low,
        # otherwise, you fill find yourself
        # checking your update condition a lot
        
        self.lock.release()
    
    async def tick(self, *, force : bool = False) -> Tuple[bool, S]:
        success, result = await super().tick(force=force)
        if success:
            await self.pos_wait()
        else:
            await self.neg_wait()
        return (success, result)
    
    async def is_new(self, shape: S) -> bool:
        exists = self.store.sismember(
            self._get_state_hash(),
            shape.hash()
        )
        if exists:
            return False
        self.store.sadd(
            self._get_state_hash(),
            shape.hash()
        )
        return True
    
    async def clean(self):
        
        self.store.flushall()