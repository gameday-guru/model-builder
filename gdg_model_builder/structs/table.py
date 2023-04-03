from ..serializer import Serializer
from typing import TypeVar, Generic, AsyncIterator, Tuple
from pydantic import BaseModel
import collections
import pandas as pd
from dask import dataframe

K = TypeVar("K")
# V = TypeVar("V")

R = TypeVar("R", bound=BaseModel)

class DataFrame(pd.DataFrame, Generic[K, R]):
    
    async def compute(self)->'DataFrame':
        """Dataframes must support lazy operations.

        Returns:
            Self: _description_
        """
        pass
    
    async def aentries(self)->AsyncIterator[Tuple[K, R]]:
        pass
        
    
class PandasDataFrame(DataFrame, pd.DataFrame):
    
    def __init__(self, *args, **kwargs) -> None:
        super(pd.DataFrame, self).__init__(*args, **kwargs)
        
    async def compute(self) -> DataFrame:
        return self
    
    async def aentries(self) -> AsyncIterator[Tuple[K, R]]:
        for [index, row] in self.itertuples():
            yield [index, row.to_dict()]
    
class DaskDataFrame(DataFrame, dataframe.DataFrame):
    
    def __init__(self, *args, **kwargs) -> None:
        super(dataframe.DataFrame, self).__init__(*args, **kwargs)
        
    async def compute(self) -> 'DataFrame':
        df = super(dataframe.DataFrame, self).compute()
        return df
    
    async def aentries(self) -> AsyncIterator[Tuple[K, R]]:
        for [index, row] in self.itertuples():
            yield [index, row.to_dict()]


class Table(Serializer[K, R], Generic[K, R]):
    
    @property
    def frame(self)->DataFrame:
        pass
    
    @frame.setter
    def df(self, df : DataFrame):
        pass
    
class DaskRedisTable(Serializer[K, R], Generic[K, R]):
    pass
    
        
class Thing(BaseModel):
    
    data : str
        
class ThingTable(Table[str, Thing]):
    pass