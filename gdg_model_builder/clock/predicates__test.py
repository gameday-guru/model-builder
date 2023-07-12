import unittest
from .predicates import secs
from datetime import datetime
from gdg_model_builder.util.deasync import deasync

class TestPredicates(unittest.TestCase):
    
    async def test_secs(self):
        
        five_secs = secs(5)
        
        first = datetime.now().timestamp() * 1000
        second = first + 1000
        third = first + 5000
        fourth = first + 7000
        fifth = first + 11000
        
        self.assertGreater(await five_secs(first), -1)
        self.assertLess(await five_secs(second), 0)
        self.assertGreater(await five_secs(third), -1)
        self.assertLess(await five_secs(fourth), 0)
        self.assertGreater(await five_secs(fifth), -1)