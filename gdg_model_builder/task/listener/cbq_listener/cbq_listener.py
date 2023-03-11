from ..listener import Listener, V
from typing import Callable, List

class CbqListener(Listener):
    
    cbq : List[Callable[[V], None]]
    
    async def listen(self) -> Callable[[Callable[[V], None]], Callable[[V], None]]:
        
        def decorator(func : Callable[[V], None]):
            self.cbq.append(func)
            return func
        
        return decorator
    
    async def call_handler(self, *, handler : Callable[[V], None], event : V):
        return handler(event)
    
    async def handle_event(self, event: V) -> None:
        
        for handler in self.cbq:
            await handler(event)
        
