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
        ts : float
        encoding : str = "UTF-8"
        
        def __init__(self, *, val : str) -> None:
            super().__init__()
            self.val = val
            self.ts = datetime.datetime.now().timestamp()
            
            
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
        
        def get_ts(self) -> float:
            return self.ts
        
    
    @deasync
    async def test_pushes_time_dependent(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        
        t0 = self.StrShape(val="Hello")
        await schedule.push_time_dependent(shape=t0)
        res = await schedule.pop_time_dependent()
        self.assertEqual(res, t0.val)
        
    @deasync
    async def test_multi_pushes_time_dependent(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t0 = self.StrShape(val="Hello")
        t1 = self.StrShape(val="World")
        await schedule.push_time_dependent(shape=t1)
        await schedule.push_time_dependent(shape=t0)
        
        res = await schedule.pop_time_dependent()
        self.assertEqual(res, t0.val)
        res = await schedule.pop_time_dependent()
        self.assertEqual(res, t1.val)
        
        await schedule.clean()
        
    @deasync
    async def test_multi_pushes_same_time_dependent(self):
        
        schedule = RedisSchedule(Shape=self.StrShape)
        await schedule.clean()
        
        t = datetime.datetime.now().timestamp()
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
        
        t0 = datetime.datetime.now().timestamp()
        t1 = datetime.datetime.now().timestamp()
        t2 = datetime.datetime.now().timestamp()
        t3 = datetime.datetime.now().timestamp()
        
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
        