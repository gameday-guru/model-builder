from typing import Callable, Awaitable, Dict, Set
from weakref import WeakKeyDictionary, WeakSet
import asyncio
from .clock import Clock, Predicate, Task


class WeakrefClock(Clock):
    tasks: Dict[
        Callable[[int], Awaitable[int]],
        Set[Callable[[int], Awaitable[None]]]
    ]

    def __init__(self) -> None:
        super().__init__()
        self.tasks = {}

    def add_task(
        self,
        *,
        predicate: Predicate,
        task: Task
    ):
        
        if predicate not in self.tasks:
            self.tasks[predicate] = set()
  
        self.tasks[predicate].add(task)

    def remove_task(
        self,
        *,
        predicate: Predicate,
        task: Task
    ):
        if predicate in self.tasks:
            self.tasks[predicate].remove(task)

    async def handle_tasks(self, *, now: int):
        futures = []
        for predicate in self.tasks.keys():
            res = await predicate(now)
            if res > 0:
                for task in self.tasks[predicate]:
                    futures.append(task(res))
        await asyncio.gather(*futures)