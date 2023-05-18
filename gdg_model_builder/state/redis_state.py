from .state import State, S
from typing import Generic
from gdg_model_builder.collection import Collection
import redis

class RedisState(State[S], Generic[S]):
    
    store : redis.Redis
    store: redis.Redis

    def __init__(
        self,
        name : str, typ : type[S], *,
        store: redis.Redis = redis.Redis()
    ) -> None:
        super().__init__(name, typ)
        self.store = store

    async def get(self) -> S:
        key = self._get_state_key()  # Get the key for the state
        value = self.store.get(key)
        
        print("GOT VALUE...", value)
        
        if value is None:
            return None
        
        # Assuming the state object has a deserialize() method
        return self.typ.deserialize(value)

    async def set(self, state: S):
        # set the state in the redis store based on something
        key = self._get_state_key()  # Get the key for the state
        value = state.serialize()  # Assuming the state object has a serialize() method

        # Store the state in Redis
        self.store.set(key, value)

        # handle the collection
        if issubclass(type(state), Collection):
            c: Collection = state
            await c.commit()
            
    def _get_state_key(self) -> str:
        # Get the typename from Shape's identify() method
        typename = self.typ.identify()
        
        # Combine typename and name to form the state key
        return f"{typename}:{self.name}"