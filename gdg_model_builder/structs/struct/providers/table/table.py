from gdg_model_builder.serializer import Serializer
from typing import TypeVar, Generic, AsyncIterator, Tuple
from pydantic import BaseModel
import pandas as pd
from dask import dataframe
from ...struct import Struct

K = TypeVar("K")
# V = TypeVar("V")

R = TypeVar("R", bound=Struct)

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


class Table(Struct, Serializer[K, R], Generic[K, R]):
    
    @property
    def frame(self)->DataFrame:
        pass
    
    @frame.setter
    def df(self, df : DataFrame):
        pass
    
    def __hash__(self) -> int:
        return sum([
            hash(val)
            for val in self.values()
        ])