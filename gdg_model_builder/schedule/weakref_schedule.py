from .schedule import Schedule, S
from weakref import WeakSet
from typing import Protocol, Callable, Awaitable, Generic

class WeakrefSchedule(Schedule, Generic[S]):
    
    cbs : WeakSet[Callable[[S], Awaitable[None]]]
    
    def __init__(self) -> None:
        super().__init__()
        self.cbs = WeakSet()
    
    async def add_handler(self, handler: Callable[[S], Awaitable[None]]):
        self.cbs.add(handler)
    
    async def remove_handler(self, handler: Callable[[S], Awaitable[None]]):
        self.cbs.remove(handler)