import unittest
from .model_struct import ModelStruct
from typing import Sequence

class TestModelStruct(unittest.TestCase):
    
    
    def test_hash(self):
        
        class Thing(ModelStruct):
            a : str
            b : int
            
        t = Thing(a="hello", b=3)
        print(t.struct_hash())
        
        self.assertEquals(t.struct_hash(), t.struct_hash())
        
    def test_big_hash(self):
        
        class Thing(ModelStruct):
            a : str
            b : Sequence[int]
            
        t = Thing(a="hello", b=[i for i in range(0, 1_000_000)])
        print(t.struct_hash())
        
        self.assertEquals(t.struct_hash(), t.struct_hash())