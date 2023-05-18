import unittest
from gdg_model_builder.util.deasync import deasync
from gdg_model_builder.shape import PydanticShape
from .redis_watcher import RedisWatcher

class Hello(PydanticShape):
    to : str
    
class HelloEvent(PydanticShape):
    to : str


class TestRedisWatcher(unittest.TestCase):
    
    @deasync
    async def test_redis_watcher(self):
        
        async def observor(*args):
            return Hello(to="Liam")
        async def translator(*args):
            return HelloEvent(to="Liam")    
        
        watcher = RedisWatcher(
            shape=Hello,
            event=HelloEvent,
            observer=observor,
            translator=translator
        )
    
        for i in range(20):
            await watcher.tick()