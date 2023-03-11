import polars
from ..serializer import Serializer
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel
import collections

K = TypeVar("K")
# V = TypeVar("V")

R = TypeVar("R", bound=BaseModel)

class Table(collections.UserDict[K, R], Generic[K, R]):
    
    serializer : Serializer
    frame : polars.DataFrame
    
    def __init__(self, *, mapping : Optional[Serializer] = None) -> None:
        """_summary_

        Args:
            mapping (Serializer): _description_
        """
        self.mapping = mapping or Serializer()
        self.frame = polars.DataFrame(mapping)
        
class Thing(BaseModel):
    
    data : str
        
class ThingTable(Table[str, Thing]):
    pass