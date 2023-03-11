from ..listener import Listener, V
from typing import Callable, List
from time import sleep

class SleepyListener(Listener):
    
    sleep : int
    
    def __init__(self, *, sleep : int = 0) -> None:
        super().__init__()
        self.sleep == sleep
    
    async def should_proceed(self) -> bool:
        sleep(self.sleep)