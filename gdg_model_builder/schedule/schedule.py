from typing import Protocol, Callable, Awaitable, Generic, TypeVar
from gdg_model_builder.shape import Shape

S = TypeVar("S", bound=Shape)

class Schedule(Protocol, Generic[S]):
    
    async def emit(self, *, shape : Shape, force : bool = False)->bool:
        pass
    
    async def add_handler(self, handler : Callable[[S], Awaitable[None]], shape : type[S]):
        pass
    
    async def remove_handler(self, handler : Callable[[S], Awaitable[None]], shape : type[S]):
        pass
    
    async def done(self, shape : S):
        pass
    
    async def listen(self):
        pass