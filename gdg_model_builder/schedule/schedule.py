from typing import Protocol, Callable, Awaitable, Generic, TypeVar
from gdg_model_builder.shape import Shape

S = TypeVar("S", bound=Shape)

class Schedule(Protocol, Generic[S]):
    
    async def emit(self, *, shape : S, force : bool = False)->bool:
        pass
    
    async def add_handler(self, handler : Callable[[S], Awaitable[None]]):
        pass
    
    async def remove_handler(self, handler : Callable[[S], Awaitable[None]]):
        pass
    
    async def done(self, shape : S):
        pass
    
    async def tick(self):
        pass