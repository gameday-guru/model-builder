import polars
from ..serializer import Serializer
from typing import TypeVar, Generic
from pydantic import BaseModel

R = TypeVar("R", BaseModel)

class Table(Generic[R]):
    
    mapping : Serializer
    
    def __init__(self, *, mapping : Serializer) -> None:
        """_summary_

        Args:
            mapping (Serializer): _description_
        """
        self.mapping = mapping
        self.data_frame = polars.DataFrame(mapping)