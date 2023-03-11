import collections
from enum import Enum
from typing import Sequence, TypeVar, Generic, Dict, Tuple, Iterable, Optional, Protocol, Tuple, Callable

K = TypeVar("K")
V = TypeVar("V")

class Listener(Protocol, Generic[V]):
    
    async def listen(self)->Callable[
        [Callable[[V], None]],
        Callable[[V], None]
    ]:
        pass
    
    async def should_proceed(self)->bool:
        pass
    
    async def handle_event(self, event : V)->None:
        pass
    
    async def get_events(self)->Iterable[V]:
        pass  
    
    async def run(self):
        
        while await self.should_proceed():
            for event in self.get_events():
                await self.handle_event(event)
             
            
  