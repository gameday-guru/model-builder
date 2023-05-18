from gdg_model_builder.shape import Shape, PydanticShape
import pandas as pd
from typing import TypeVar, Generic, Optional
import collections
import math
import numpy as np
from typing_extensions import Self

V = TypeVar("V", bound=Shape)

class CollectionData(PydanticShape):
    name : str
    size : int

class DataFrame(pd.DataFrame):
    
    async def gather(self):
        pass

class Collection(Shape, collections.UserDict[str, V], Generic[V]):
    
    shape : type[V]
    name : str
    
    def __init__(self, *, name : str):
        super.__init__(self)
        self.name = name
    
    async def hash(self) -> bytes:
        size = self.size
        sample_size = 16 * math.log(2, size)
        step = int(size/sample_size)
        next_step = 0
        rng = np.random.default_rng(42)
        acc = bytes(f"{size}", encoding="UTF-8")
        for i, t in enumerate(self.values()):
            if i == next_step:
                acc += t.hash()
                next_step = int(i + (step * rng.random()))
        return acc
    
    def serialize(self) -> bytes:
        return CollectionData(size=self.size, name=self.name).serialize()
    
    @classmethod
    def deserialize(cls, serial: bytes) -> Self:
        data = CollectionData.deserialize(serial)
        return cls(
            name=data.name
        )
    
    @property
    def frame(self)->DataFrame:
        pass
    
    @property
    def size(self)->int:
        pass
    
    async def commit(self, *, frame : Optional[DataFrame] = None):
        pass
