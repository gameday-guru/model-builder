from ...struct import Struct
import json
import numpy as np
import random
import math

class ModelStruct(Struct):
    
    def struct_hash(self) -> bytes:
        
        abs = bytearray(json.dumps(self.dict()), encoding="utf-8")
        arr = np.frombuffer(abs, dtype="int8")
        rng = np.random.default_rng(arr.size)
        rng.shuffle(arr)
        return rng.choice(
            arr, 
            int(16 * math.log2(arr.size))
        ).tobytes()