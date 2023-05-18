from gdg_model_builder.collection.collection import DataFrame
from .collection import Collection, V
from gdg_model_builder.shape import Shape
from typing import Iterable, Generic, Optional, Tuple, Dict
import redis
from typing_extensions import Self

class RedisCollection(Collection[V], Generic[V]):
    
    shape : type[V]
    store : redis.Redis
    name : str
    buffer_size : int
    local_changes : Dict[str, V]
    
    def __init__(
        self, 
        *, 
        store : redis.Redis = redis.Redis(),
        name : str = "root"
    ):
        # super().__init__(name=name)
        self.store = store
        self.name = name
        self.local_changes= {}
        
    def _get_state_key(self) -> str:
        # Get the typename from Shape's identify() method
        typename = self.shape.identify()
        
        # Combine typename and name to form the state key
        name = f"{typename}:{self.name}"
        return name
    
    def __getitem__(self, key : str):
        
        res = self.store.hget(
            self._get_state_key(),
            key
        )
        
        if res is not None:
            return self.shape.deserialize(res)
        
        return self.local_changes.get(key, None)

    def __setitem__(self, key : str, value : V):
        self.local_changes[key] = value
        

    def __delitem__(self, key):
        self.store.hdel(
            self._get_state_key(),
            key
        )

    def __contains__(self, key):
        self.store.hexists(
            self._get_state_key(),
            key
        )
    
    def keys(self) -> Iterable[str]:

        for key, _ in self.items():
            yield key
    
    def items(self) -> Iterable[Tuple[str, V]]:
 
        for key, val in self.store.hscan_iter(self._get_state_key()):
            yield (key, self.shape.deserialize(val))
        
    def values(self) -> Iterable[V]:

        for _, value in self.items():
            yield value
            
    @property
    def size(self) -> int:
        return int(self.store.hlen(self._get_state_key()))
            
    async def commit(self, *, frame: DataFrame | None = None):
        
        if frame is not None:
            for k, row in frame.iterrows(): # can we do iterrows
                val = self.shape.from_dict(**row)
                if [self[k].hash()] == val.hash():
                    continue
                self.local_changes[k] = val

        for key, val in self.local_changes.items():
            self.store.hset(
                self._get_state_key(),
                key,
                val.serialize()
            )
            