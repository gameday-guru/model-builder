from gdg_model_builder.serializer import Serializer
from typing import TypeVar, Generic, AsyncIterator, Tuple
from pydantic import BaseModel, Field
import pandas as pd
from dask import dataframe, delayed
from ...struct import Struct
import math
import numpy as np
from typing import Iterable, Dict
from ..model_struct import ModelStruct

K = TypeVar("K")
R = TypeVar("R", bound=ModelStruct)

class DataFrame(pd.DataFrame, Generic[K, R]):
    
    async def compute(self)->'DataFrame':
        """Dataframes must support lazy operations.

        Returns:
            Self: _description_
        """
        pass
    
    async def aentries(self)->AsyncIterator[Tuple[K, R]]:
        pass
        
    
class PandasDataFrame(DataFrame[K, R], pd.DataFrame, Generic[K, R]):
    
    def __init__(self, *args, **kwargs) -> None:
        super(pd.DataFrame, self).__init__(*args, **kwargs)
        
    async def compute(self) -> DataFrame:
        return self
    
    async def aentries(self) -> AsyncIterator[Tuple[K, R]]:
        for [index, row] in self.itertuples():
            yield [index, row.to_dict()]
    
class DaskDataFrame(DataFrame[K, R], dataframe.DataFrame, Generic[K, R]):
    
    def __init__(self, *args, **kwargs) -> None:
        super(dataframe.DataFrame, self).__init__(*args, **kwargs)
        
    async def compute(self) -> 'DataFrame':
        df = super(dataframe.DataFrame, self).compute()
        return df
    
    async def aentries(self) -> AsyncIterator[Tuple[K, R]]:
        for [index, row] in self.itertuples():
            yield [index, row.to_dict()]


class Table(Struct, Serializer[K, R], Generic[K, R]):
    
    serializer : Serializer[K, R]
    
    @property
    def frame(self)->DataFrame:
        pass
    
    @frame.setter
    def frame(self, df : DataFrame):
        pass
    
    def __init__(self, *, serializer : Serializer[K, R]) -> None:
        super().__init__()
        self.serializer = serializer
        
    
    def struct_hash(self) -> bytes:
        """Hashes the struct.
        
        NOTE: this is the protocol for hasing a table, not a bespoke implementation,
        hence it is implement at the protocol level of abstraction.

        Returns:
            bytes: _description_
        """
        size = self.size()
        sample_size = 16 * math.log(2, size)
        step = int(size/sample_size)
        next_step = 0
        rng = np.random.default_rng(42)
        acc = bytes(f"{size}", encoding="UTF-8")
        for i, t in enumerate(self.values()):
            if i == next_step:
                acc += t.struct_hash()
                next_step = int(i + (step * rng.random()))
        return acc
    
    def __getitem__(self, key):
        return self.serializer.__getitem__(key)

    def __setitem__(self, key, value):
        self.serializer.__setitem__(key, value)
        

    def __delitem__(self, key):
        self.serializer.__delitem__(key)

    # Unfortunately, __contains__ is required currently due to
    # https://github.com/python/cpython/issues/91784
    def __contains__(self, key):
        self.serializer.__contains__(key)
    
    
    def keys(self) -> Iterable[K]:
        """Gets the keys for a given state.

        Returns:
            Iterable[K]: _description_

        Yields:
            Iterator[Iterable[K]]: _description_
        """
        
        for key in self.serializer.keys():
            yield key
    
    def entries(self) -> Iterable[Tuple[K, R]]:
 
       
        # TODO: avoid de- and re-serialization
        for key, _ in self.serializer.keys():
            yield (
                key,
                self.serializer.get(key)
            )
        
    def values(self) -> Iterable[R]:

        for _, value in self.serializer.entries():
            yield value
            
    def size(self) -> int:
       return self.serializer.size()
    
    def empty(self) -> None:
       self.serializer.empty()
    
class PandasTable(Table[K, R], Generic[K, R]):
    
    pandas_data_frame : PandasDataFrame = Field(exclude=True)
    
    @property
    def frame(self)->DataFrame[K, R]:
        self.pandas_data_frame = pd.DataFrame.from_records(
            self.dict_values()
        )
        return self.pandas_data_frame
    
    @frame.setter
    def frame(self, df : DataFrame):
        self.pandas_data_frame = df
    
    def dict_values(self)->Iterable[Dict]:
        for value in self.values():
            yield value.dict()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pandas_data_frame = pd.DataFrame.from_records(
            self.dict_values()
        )
    
class DaskTable(Table[K, R], Generic[K, R]):
    
    dask_data_frame : DaskDataFrame = Field(exclude=True)
    
    def dict_values(self)->Iterable[Dict]:
        for value in self.values():
            yield value.dict()
    
    def __init__(self, *args, **kwargs) -> None:
        values_iter = self.dict_values().__iter__()
        self.dask_data_frame = dataframe.from_delayed([
            delayed(values_iter.__next__)() # this likely needs to synchronize the last read frame value here,
            # or else make this a nonce
        ])
        