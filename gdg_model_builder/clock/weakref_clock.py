from typing import Callable, Awaitable
from weakref import WeakKeyDictionary, WeakSet
import asyncio
from .clock import Clock, Predicate, Task


class WeakrefClock(Clock):
    tasks: WeakKeyDictionary[
        Callable[[int], Awaitable[int]],
        WeakSet[Callable[[int], Awaitable[None]]]
    ]

    def __init__(self) -> None:
        super().__init__()
        self.tasks = WeakKeyDictionary()

    def add_task(
        self,
        *,
        predicate: Predicate,
        task: Task
    ):
        if predicate not in self.tasks:
            self.tasks[predicate] = WeakSet()
  
        self.tasks[predicate].add(task)
        print(list(self.tasks.keys()))

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