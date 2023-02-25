import polars
from ..serializer import Serializer
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
import collections

K = TypeVar("K")
# V = TypeVar("V")

R = TypeVar("R", BaseModel)

class Table(collections.UserDict[K, R], Generic[K, R]):
    
    mapping : Serializer
    frame : polars.DataFrame[R]
    
    def __init__(self, *, mapping : Optional[Serializer]) -> None:
        """_summary_

        Args:
            mapping (Serializer): _description_
        """
        self.mapping = mapping
        self.frame = polars.DataFrame(mapping)
        
class Thing(BaseModel):
    
    data : str
        
class ThingTable(Table[str, Thing]):
    pass

tbl = ThingTable()

col2 = tbl.frame[1, ["data"]]