import collections
from enum import Enum
from typing import Sequence, TypeVar, Generic, Dict, Tuple, Iterable, Optional, Callable, Awaitable

T = TypeVar("T")

class Watcher(Generic[T]):
    
    async def get_time(self)->float:
        pass
    
    async def pos_wait(self):
        pass
    
    async def neg_wait(self):
        pass
    
    async def handle_new(self, *, new : T):
        pass
    
    async def poll(self)->Optional[T]:
        pass
    
    async def update(self)->Optional[T]:
        pass
    
    async def on_new(self, *, do : Callable[[T], Awaitable[None]]):
        pass
    
    async def watch(self):
        
        while True:
            
            res = await self.update()
            if res != None:
                await self.handle_new(new=res)
                await self.pos_wait()
                
            await self.neg_wait()