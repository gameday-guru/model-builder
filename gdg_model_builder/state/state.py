from typing import TypeVar, Generic
from gdg_model_builder.shape.shape import Shape

S = TypeVar("S", bound=Shape)

class State(Generic[S]):
    
    name : str
    typ : type[S]
    
    def __init__(self, name : str, typ : type[S]) -> None:
        super().__init__()
        self.name = name
        self.typ = typ
    
    async def get(self)->S:
        pass
    
    async def set(self, state : S):
        pass