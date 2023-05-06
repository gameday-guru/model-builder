from .state import State, S
from typing import Generic
from gdg_model_builder.collection import Collection

class RedisState(State, Generic[S]):
    
    async def get(self) -> S:
        return await super().get()
    
    async def set(self, state: S):
        
        # set the state in the redis store based on something
        
        # handle the collection
        if issubclass(type(state), Collection):
            c : Collection = state
            await c.commit()