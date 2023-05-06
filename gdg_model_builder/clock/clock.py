from typing import Callable, Awaitable

Predicate = Callable[[int], Awaitable[int]]
Task = Callable[[int], Awaitable[None]]

class Clock:
    
    def now(self)->int:
        pass
    
    def add_task(
        self, *,  
        predicate : Predicate,
        task : Task
    ):
        pass
    
    def remove_task(
        self, *,  
        predicate : Predicate,
        task : Task
    ):
        pass
    
    async def handle_tasks(self, *, now : int):
        pass
    
    async def tick(self):
        await self.handle_tasks(now=self.now())
        
        