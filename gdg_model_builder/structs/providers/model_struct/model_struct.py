from ...struct import Struct
from pydantic import BaseModel
import json
import numpy as np
import math

class ModelStruct(Struct, BaseModel):
    
    def struct_hash(self) -> bytes:
        """Produces a bytes hash of arbitrary length of the struct.
        
        WARN: the runtime on this is currently rather slow owing to the 
        the shuffle.
        UPDATE: the above was improved slighly by using permutation instead.

        Returns:
            bytes: _description_
        """
        
        abs = bytearray(json.dumps(self.dict()), encoding="utf-8")
        arr = np.frombuffer(abs, dtype="int8")
        rng = np.random.default_rng(arr.size)
        perm = arr[rng.permutation(arr.size)]
        return rng.choice(
            perm, 
            int(16 * math.log2(arr.size))
        ).tobytes()