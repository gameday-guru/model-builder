import unittest
from .model_struct import ModelStruct
from typing import Sequence
from time import perf_counter
import math
import numpy as np


class TestModelStruct(unittest.TestCase):
    
    
    def test_hash(self):
        
        class Thing(ModelStruct):
            a : str
            b : int
            
        t = Thing(a="hello", b=3)
        
        self.assertEquals(t.struct_hash(), t.struct_hash())
        
    def test_big_hash(self):
        
        class Thing(ModelStruct):
            a : str
            b : Sequence[int]
            
        t = Thing(a="hello", b=[i for i in range(0, 1_000_000)])
        # print(t.struct_hash())
        
        self.assertEquals(t.struct_hash(), t.struct_hash())
        
    def test_many_avg_hash(self):
        
        class Thing(ModelStruct):
            game_id : str
            home_score : int
            away_score : int
            home_id : str
            away_id : str
            
        things = [
            Thing(
                game_id="1234nsf",
                home_id="234sdfhksdf",
                away_id="sdfhksadf2",
                home_score=382,
                away_score=234
            ) for i in range(0, 1_000_000)
        ]
        
        
        t0 = perf_counter()
        sample_size = 16 * math.log(2, 1_000_000)
        step = int(1_000_000/sample_size)
        next_step = 0
        rng = np.random.default_rng(42)
        for i, t in enumerate(things):
            if i == next_step:
                t.struct_hash()
                next_step = int(i + (step * rng.random()))
            
        t1 = perf_counter()
        print(t1-t0)