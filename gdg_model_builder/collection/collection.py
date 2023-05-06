from gdg_model_builder.shape import Shape
import pandas as pd
from typing import TypeVar, Generic
import collections

K = TypeVar("K")
V = TypeVar("V")


class DataFrame(pd.DataFrame):
    
    async def gather(self):
        pass

class Collection(Shape, DataFrame, collections.UserDict[K, V], Generic[K, V]):
    
    @property
    def frame(self)->DataFrame:
        pass
    
    async def commit(self):
        pass