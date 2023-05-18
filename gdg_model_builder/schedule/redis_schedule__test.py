import unittest
from gdg_model_builder.util.deasync import deasync
from .redis_schedule import RedisSchedule
from gdg_model_builder.shape import Shape
import datetime
from typing_extensions import Self
import asyncio

class TestRedisSchedule(unittest.TestCase):
    
    class StrShape(Shape):
        
        val : str
        ts : int
        encoding : str = "UTF-8"
        
        def __init__(self, *, val : str) -> None:
            super().__init__()
            self.val = val
            self.ts = int(datetime.datetime.now().timestamp() * 1000)
            
            
        def serialize(self) -> bytes:
            return bytes(self.val,encoding=self.encoding)
        
        @classmethod
        def identify(cls) -> bytes:
            return b'StrShape'
        
        @classmethod
        def deserialize(cls, serial: bytes) -> Self:
            return bytes.decode(serial, encoding=cls.encoding)
        
        def hash(self) -> bytes:
            return bytes(self.val, encoding=self.encoding)
        
        def get_ts(self) -> int:
            return self.ts
        
    
    @deasync
    async def test_pushes_time_dependent(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t0 = self.StrShape(val="Hello")
        await schedule.push_time_dependent(shape=t0)
        res = await schedule.pop_time_dependent()
        self.assertEqual(res, t0.val)
        await schedule.clean()
        
    @deasync
    async def test_multi_pushes_same_time_dependent(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t = int(datetime.datetime.now().timestamp() * 1000)
        t0 = self.StrShape(val="Hello")
        t1 = self.StrShape(val="World")
        t0.ts = t
        t1.ts = t
        await schedule.push_time_dependent(shape=t1)
        await schedule.push_time_dependent(shape=t0)
        
        res = await schedule.pop_time_dependent()
        self.assertEqual(res, t1.val)
        res = await schedule.pop_time_dependent()
        self.assertEqual(res, t0.val)
        
        await schedule.clean()
        
    @deasync
    async def test_lots_of_pushes_time_dependent(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t0 = int(datetime.datetime.now().timestamp() * 1000)
        t1 = t0 + 1
        t2 = t1 + 1
        t3 = t2 +1
        
        for i in range(0, 100):
            first_order = self.StrShape(val="first_Hello")
            first_order.ts = t0
            
            second_order = self.StrShape(val="second_World")
            second_order.ts = t1
            
            third_order = self.StrShape(val="third_of")
            third_order.ts = t2
            
            fourth_order = self.StrShape(val="fourth_Mine")
            fourth_order.ts = t3
            
            await asyncio.gather(
                schedule.push_time_dependent(shape=first_order),
                schedule.push_time_dependent(shape=second_order),
                schedule.push_time_dependent(shape=third_order),
                schedule.push_time_dependent(shape=fourth_order),
            )
            
        for i in range(0, 400):
            res : str = await schedule.pop_time_dependent()
            if i < 100:
                self.assertTrue(res.startswith("first"))
            elif i < 200:
                self.assertTrue(res.startswith("second"))
            elif i < 300:
                self.assertTrue(res.startswith("third"))
            elif i < 400:
                self.assertTrue(res.startswith("fourth"))
            
        await schedule.clean()
        
    @deasync
    async def test_tick(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t0 = int(datetime.datetime.now().timestamp() * 1000)
        t1 = t0 + 1
        t2 = t1 + 1
        t3 = t2 +1
        
        first_count = 0
        second_count = 0
        third_count = 0
        fourth_count = 0
        async def handle_str_shape(*args):
            nonlocal first_count
            nonlocal second_count
            nonlocal third_count
            nonlocal fourth_count
            if args[0] == "first_Hello":
                first_count += 1
            elif args[0] == "second_World":
                second_count += 1
            elif args[0] == "third_of":
                third_count += 1
            elif args[0] == "fourth_Mine":
                fourth_count += 1
            
            
        await schedule.add_handler(handle_str_shape)
        
        for _ in range(0, 10):
            first_order = self.StrShape(val="first_Hello")
            first_order.ts = t0
            
            second_order = self.StrShape(val="second_World")
            second_order.ts = t1
            
            third_order = self.StrShape(val="third_of")
            third_order.ts = t2
            
            fourth_order = self.StrShape(val="fourth_Mine")
            fourth_order.ts = t3
            
            await asyncio.gather(
                schedule.push_time_dependent(shape=first_order),
                schedule.push_time_dependent(shape=second_order),
                schedule.push_time_dependent(shape=third_order),
                schedule.push_time_dependent(shape=fourth_order),
            )
            
        for i in range(0, 10):
            await schedule.tick()
            self.assertEqual(i + 1, first_count)
            
        for i in range(0, 10):
            await schedule.tick()
            self.assertEqual(i + 1, second_count)
        
        for i in range(0, 10):
            await schedule.tick()
            self.assertEqual(i + 1, third_count)
            
        for i in range(0, 10):
            await schedule.tick()
            self.assertEqual(i + 1, fourth_count)
            
        await schedule.clean()
        
    @deasync
    async def test_emit_and_tick(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t0 = int(datetime.datetime.now().timestamp() * 1000)
        t1 = t0 + 1
        t2 = t1 + 1
        t3 = t2 +1
        
        first_count = 0
        second_count = 0
        third_count = 0
        fourth_count = 0
        async def handle_str_shape(*args):
            nonlocal first_count
            nonlocal second_count
            nonlocal third_count
            nonlocal fourth_count
            if args[0] == "first_Hello":
                first_count += 1
            elif args[0] == "second_World":
                second_count += 1
            elif args[0] == "third_of":
                third_count += 1
            elif args[0] == "fourth_Mine":
                fourth_count += 1
            
            
        await schedule.add_handler(handle_str_shape)
        
        for _ in range(0, 10):
            first_order = self.StrShape(val="first_Hello")
            first_order.ts = t0
            
            second_order = self.StrShape(val="second_World")
            second_order.ts = t1
            
            third_order = self.StrShape(val="third_of")
            third_order.ts = t2
            
            fourth_order = self.StrShape(val="fourth_Mine")
            fourth_order.ts = t3
            
            await asyncio.gather(
                schedule.emit(shape=first_order),
                schedule.emit(shape=second_order),
                schedule.emit(shape=third_order),
                schedule.emit(shape=fourth_order),
            )
            
        for i in range(0, 10):
            await schedule.tick()
        
        self.assertEqual(1, first_count)
        self.assertEqual(1, second_count)
        self.assertEqual(1, third_count)
        self.assertEqual(1, fourth_count)
            
        await schedule.clean()
        
    @deasync
    async def test_emit_and_tick_diff(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t0 = int(datetime.datetime.now().timestamp() * 1000)
        t1 = t0 + 1
        t2 = t1 + 1
        t3 = t2 +1
      
        
        first_count = 0
        second_count = 0
        third_count = 0
        fourth_count = 0
        async def handle_str_shape(*args):
            nonlocal first_count
            nonlocal second_count
            nonlocal third_count
            nonlocal fourth_count
            if args[0].startswith("first_Hello"):
                first_count += 1
            elif args[0].startswith("second_World"):
                second_count += 1
            elif args[0].startswith("third_of"):
                third_count += 1
            elif args[0].startswith("fourth_Mine"):
                fourth_count += 1
            
            
        await schedule.add_handler(handle_str_shape)
        
        for i in range(0, 10):
            first_order = self.StrShape(val=f"first_Hello_{i}")
            first_order.ts = t0
            
            second_order = self.StrShape(val=f"second_World_{i}")
            second_order.ts = t1
            
            third_order = self.StrShape(val=f"third_of_{i}")
            third_order.ts = t2
            
            fourth_order = self.StrShape(val=f"fourth_Mine_{i}")
            fourth_order.ts = t3
            
            await asyncio.gather(
                schedule.emit(shape=first_order),
                schedule.emit(shape=second_order),
                schedule.emit(shape=third_order),
                schedule.emit(shape=fourth_order),
            )
            
        for i in range(0, 10):
            await schedule.tick()
        
        self.assertEqual(10, first_count)
        self.assertEqual(0, second_count)
        self.assertEqual(0, third_count)
        self.assertEqual(0, fourth_count)
        
        for i in range(0, 10):
            await schedule.tick()
            
        self.assertEqual(10, first_count)
        self.assertEqual(10, second_count)
        self.assertEqual(0, third_count)
        self.assertEqual(0, fourth_count)
        
        for i in range(0, 10):
            await schedule.tick()
            
        self.assertEqual(10, first_count)
        self.assertEqual(10, second_count)
        self.assertEqual(10, third_count)
        self.assertEqual(0, fourth_count)
        
        for i in range(0, 10):
            await schedule.tick()
            
        self.assertEqual(10, first_count)
        self.assertEqual(10, second_count)
        self.assertEqual(10, third_count)
        self.assertEqual(10, fourth_count)
            
        await schedule.clean()
        