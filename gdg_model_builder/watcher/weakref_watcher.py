from .watcher import Watcher, T
from weakref import WeakSet
from typing import Generic, Awaitable, Callable

class WeakRefWatcher(Watcher[T], Generic[T]):
    
    cbs : WeakSet[Callable[[T], Awaitable[None]]]
    
    async def handle_new(self, *, new: T):
        for cb in self.cbs:
            await cb(new)
            
    async def on_new(self, *, do: Callable[[T], Awaitable[None]]):
        self.cbs.add(do)