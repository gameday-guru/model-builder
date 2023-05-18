import unittest
from gdg_model_builder.util.deasync import deasync
from .redis_multiplexed_schedule import RedisMultiplexedSchedule
from gdg_model_builder.shape.pydantic_shape import PydanticShape
import datetime
from typing_extensions import Self
import asyncio

class A(PydanticShape):
    a : str
    
class B(PydanticShape):
    b : str

class TestRedisSchedule(unittest.TestCase):
                 
    @deasync
    async def test_emit_and_tick(self):
        
        schedule = RedisMultiplexedSchedule()
        await schedule.clean()
        
        first_count = 0
        second_count = 0
        third_count = 0
        fourth_count = 0
      
        
        first_a_count = 0
        second_a_count = 0
        third_a_count = 0
        fourth_a_count = 0
        
        
        async def handle_a_shape(shape : A):
            
            nonlocal first_count
            nonlocal second_count
            nonlocal third_count
            nonlocal fourth_count
            
            nonlocal first_a_count
            nonlocal second_a_count
            nonlocal third_a_count
            nonlocal fourth_a_count
            
            if shape.a.startswith("first_Hello"):
                first_count += 1
                first_a_count +=1 
            elif shape.a.startswith("second_World"):
                second_count += 1
                second_a_count += 1
            elif shape.a.startswith("third_of"):
                third_count += 1
                third_a_count += 1
            elif shape.a.startswith("fourth_Mine"):
                fourth_count += 1
                fourth_a_count += 1
           
        b_first_count = 0
        b_last_count = 0     
        async def handle_b_shape(shape : B):
            
            nonlocal b_first_count
            nonlocal b_last_count
            
            if shape.b == "first":
                b_first_count += 1
            
            if shape.b == "last":
                b_last_count += 1
            
            
            
        await schedule.add_handler(handle_a_shape, A)
        await schedule.add_handler(handle_b_shape, B)
        await schedule.clean()
        
        first_order = A(a=f"first_Hello_")
        second_order = A(a=f"second_World_")
        second_order._ts = first_order._ts + 1
        third_order = A(a=f"third_of_")
        third_order._ts = second_order._ts + 1
        fourth_order = A(a=f"fourth_Mine_")
        fourth_order._ts = third_order._ts + 1
        
        b_first = B(b="first")
        b_first._ts = first_order._ts
        
        b_last = B(b="last")
        b_last._ts = fourth_order._ts + 1
        
        for i in range(0, 10):
            
            first_order.a = f"first_Hello_{i}"
            second_order.a =f"second_World_{i}"
            third_order.a = f"third_of_{i}"
            fourth_order.a= f"fourth_Mine_{i}"
        
            await asyncio.gather(
                schedule.emit(shape=first_order),
                schedule.emit(shape=second_order),
                schedule.emit(shape=third_order),
                schedule.emit(shape=fourth_order),
                schedule.emit(shape=b_first),
                schedule.emit(shape=b_last)
            )
            
        for i in range(0, 10):
            await schedule.tick()
        
        self.assertEqual(10, first_count)
        self.assertEqual(0, second_a_count)
        self.assertEqual(0, third_count)
        self.assertEqual(0, fourth_count)
        self.assertEqual(1, b_first_count)
        self.assertEqual(0, b_last_count)
        
        for i in range(0, 10):
            await schedule.tick()
        
        self.assertEqual(10, first_count)
        self.assertEqual(10, second_a_count)
        self.assertEqual(0, third_count)
        self.assertEqual(0, fourth_count)
        self.assertEqual(1, b_first_count)
        self.assertEqual(0, b_last_count)
        
        for i in range(0, 10):
            await schedule.tick()
        
        self.assertEqual(10, first_count)
        self.assertEqual(10, second_a_count)
        self.assertEqual(10, third_count)
        self.assertEqual(0, fourth_count)
        self.assertEqual(1, b_first_count)
        self.assertEqual(0, b_last_count)
        
        for i in range(0, 10):
            await schedule.tick()
        
        self.assertEqual(10, first_count)
        self.assertEqual(10, second_a_count)
        self.assertEqual(10, third_count)
        self.assertEqual(10, fourth_count)
        self.assertEqual(1, b_first_count)
        self.assertEqual(1, b_last_count)
            
        await schedule.clean()
        