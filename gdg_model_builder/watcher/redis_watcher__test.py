import unittest
from gdg_model_builder.util.deasync import deasync
from gdg_model_builder.shape import PydanticShape
from .redis_watcher import RedisWatcher
import datetime

class Hello(PydanticShape):
    to : str
    
class HelloEvent(PydanticShape):
    to : str


class TestRedisWatcher(unittest.TestCase):
    
    @deasync
    async def test_redis_watcher(self):
        
        obs_count = 0
        async def observor(*args):
            nonlocal obs_count
            obs_count += 1
            return Hello(to="Liam")
        trans_count = 0
        async def translator(*args):
            nonlocal trans_count
            trans_count += 1
            return HelloEvent(to="Liam")    
        
        watcher = RedisWatcher(
            shape=Hello,
            event=HelloEvent,
            observer=observor,
            translator=translator
        )
        await watcher.clean()
    
        for i in range(20):
            await watcher.tick()
            
        self.assertEqual(obs_count, 20)
        self.assertEqual(trans_count, 1)
        
    @deasync
    async def test_redis_watcher_front_heavy(self):
        
        obs_count = 0
        async def observor(*args):
            nonlocal obs_count
            obs_count += 1
            return Hello(to=f"Liam {obs_count % 5}")
        trans_count = 0
        async def translator(*args):
            nonlocal trans_count
            trans_count += 1
            return HelloEvent(to=f"Liam {trans_count}")    
        
        watcher = RedisWatcher(
            shape=Hello,
            event=HelloEvent,
            observer=observor,
            translator=translator
        )
        await watcher.clean()
    
        for i in range(20):
            await watcher.tick()
            
        self.assertEqual(obs_count, 20)
        self.assertEqual(trans_count, 5)
        
        print(watcher.mean_time)
        
    @deasync
    async def test_redis_watcher_scattered(self):
        
        obs_count = 0
        async def observor(*args):
            nonlocal obs_count
            obs_count += 1
            return Hello(to=f"Liam {int(datetime.datetime.now().timestamp() * 10) % 5}")
        trans_count = 0
        async def translator(*args):
            nonlocal trans_count
            trans_count += 1
            return HelloEvent(to=f"Liam {trans_count}")    
        
        watcher = RedisWatcher(
            shape=Hello,
            event=HelloEvent,
            observer=observor,
            translator=translator
        )
        await watcher.clean()
    
        for i in range(20):
            await watcher.tick()
            
        self.assertEqual(obs_count, 20)
        self.assertLessEqual(trans_count, 20)
        
        print(watcher.mean_time)