from .clock import Clock
from typing import Callable, Awaitable
from datetime import datetime
from .weakref_clock import WeakrefClock

class RetroClock(WeakrefClock):
    
    step : int
    retrodating : bool
    internal_time : int
    
    def __init__(
        self, *, 
        step : int = 1000,
        start : int = int(datetime.now().timestamp() * 1000) - (1000 * 1000) # second ago
    ) -> None:
        super().__init__()
        self.step = step
        self.internal_time = start
        self.retrodating = False
    
    def now(self)->int:
        
        return int(datetime.now().timestamp() * 1000) if self.retrodating else self.internal_time
 
    async def tick(self):
        await super().tick()
        self.internal_time += self.step
        if self.internal_time > int(datetime.now().timestamp() * 1000):
            self.retrodating = False
        