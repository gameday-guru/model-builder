from .watcher import Watcher, T
from asyncio import sleep
from asyncio.locks import Lock
import math
from datetime import datetime
from typing import Generic

class LogMeanWatcher(Watcher[T], Generic[T]):
    
    mean_time : float
    finds : int
    last_time : float
    sleep : float
    lock : Lock
    base : int
    
    def __init__(self) -> None:
        super().__init__()
        self.mean_time = 1
        self.finds = 0
        self.last_time = datetime.now().timestamp()
        self.sleep = 1
        self.lock = Lock()
        self.base = 2
        
    async def neg_wait(self):
        await sleep(self.sleep)
    
    async def pos_wait(self):
        
        # sleep however long the last step determined we should
        await self.neg_wait()
        
        # get the time from our internally represented clock
        t = await self.get_time()
        
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
        
    async def watch(self):
        self.last_time = datetime.now().timestamp()
        return await super().watch()
        