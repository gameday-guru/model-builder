import unittest
from gdg_model_builder.util.deasync import deasync
from .retro_clock import RetroClock
from .predicates import secs

class TestRedisSchedule(unittest.TestCase):
        
    @deasync
    async def test_lots_of_pushes_time_dependent(self):
        
        clock = RetroClock(step=1000*1000)
        
        count = 0
        async def say_hello(now : int):
            nonlocal count
            count += 1
            
        interval = secs(2) # for weakref
        clock.add_task(
            predicate=interval,
            task=say_hello
        )
        
        await clock.tick()
        await clock.tick()
        
        self.assertEqual(count, 1)
        
        
    
        
        