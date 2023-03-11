import unittest
from .lru import lru_cache_time
import time
import datetime


class LruTest(unittest.TestCase):
    
    def test_lru_multiply(self):
        
        count = 0
        @lru_cache_time(1, 64)
        def multiply(a : int, b : int)->int:
            nonlocal count
            count += 1
            return a * b
        
        for i in range(10):
            self.assertEquals(multiply(2, 2), 4)
            self.assertEquals(count, 1)
        
        time.sleep(1)
        for i in range(10):
            self.assertEquals(multiply(2, 2), 4)
            self.assertEquals(count, 2)
        
    def test_lru_datetime(self):
        
       pass
        
        
        