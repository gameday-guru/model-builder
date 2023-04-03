import unittest
from .log_mean_watcher import LogMeanWatcher
from typing import Optional
from datetime import datetime
from gdg_model_builder.libutil.sync.deasync import deasync

class TestLogMeanWatcher(unittest.TestCase):
    
    class Ticks(LogMeanWatcher[float]):
        
        def __init__(self) -> None:
            super().__init__()
            
        async def get_time(self) -> float:
            return datetime.now().timestamp()
        
        async def update(self) -> Optional[float]:
            ts = datetime.now().timestamp() 
            print(int(ts) % 3)
            if (int(ts) % 3) == 0:
                return ts
            return None
        
        async def handle_new(self, *, new: float):
            ts = datetime.now()
            print(datetime.now(), ts.timestamp(), new, self.sleep, self.mean_time)
    
    @deasync
    async def test_watch(self):
        
        watcher = self.Ticks()
        
        await watcher.watch()
        
        
