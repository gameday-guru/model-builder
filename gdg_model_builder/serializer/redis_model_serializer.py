from .model_serializer import ModelSerializer
from typing import Sequence, TypeVar, Generic, Tuple, Iterable, Mapping
import redis

K = TypeVar("K")
V = TypeVar("V")

class RedisModelSerializer(ModelSerializer[K, V],  Generic[K, V]):
    
    store : redis.Redis
    buffer : int = 32
    encoding : str = "utf-8"
    
    def __init__(self, *args, store : redis.Redis, model_name : str, state_name : str, **kwargs) -> None:
        """Initializers a model serializer with a model_name and state_name.

        Args:
            model_name (str): is the name of the model.
            state_name (str): is the name of the state to which this applies.
        """
        super().__init__(*args, model_name=model_name,state_name=state_name, **kwargs)
        self.store = store
    
    def __getitem__(self, key):
        """_summary_

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        serialized = self.store.get(self.model_hash(key))
        if serialized is None:
            return None
        return self.deserialize(serialized)

    def __setitem__(self, key, value):
        """_summary_

        Args:
            key (_type_): _description_
            value (_type_): _description_
        """
        
        model_state_key = self.get_model_state_hash()
        entry_key = self.model_hash(key)
        
        self.store.zadd(model_state_key, { entry_key : 0})
        self.store.set(entry_key, self.serialize(value))
        

    def __delitem__(self, key):
        """_summary_

        Args:
            key (_type_): _description_
        """
        model_state_key = self.get_model_state_hash()
        entry_key = self.model_hash(key)
        
        self.store.zrem(model_state_key, entry_key)
        self.store.delete(entry_key)

    # Unfortunately, __contains__ is required currently due to
    # https://github.com/python/cpython/issues/91784
    def __contains__(self, key):
        
        entry_key = self.model_hash(key)
        return self.store.exists(entry_key) > 0
    
    def _keys(self)->Iterable[Tuple[K, bytes]]:
        
        model_state_key = self.get_model_state_hash()
        
        start = 0
        while rkeys := self.store.zrange(model_state_key, start, start + self.buffer):
            for rkey in rkeys:
                yield (self.model_unhash(rkey), rkey)
            start += self.buffer
    
    def keys(self) -> Iterable[K]:
        """Gets the keys for a given state.

        Returns:
            Iterable[K]: _description_

        Yields:
            Iterator[Iterable[K]]: _description_
        """
        
        for key, _ in self._keys():
            yield key
    
    def entries(self) -> Iterable[Tuple[K, V]]:
        """Gets the entries in order using a buffer.

        Returns:
            Iterable[Tuple[K, V]]: _description_

        Yields:
            Iterator[Iterable[Tuple[K, V]]]: _description_
        """
        
        # TODO: avoid de- and re-serialization
        for key, _ in self._keys():
            yield (
                key,
                self.get(key)
            )
        
    def values(self) -> Iterable[V]:
        """Produces a values iterable for the table

        Returns:
            Iterable[V]: _description_

        Yields:
            Iterator[Iterable[V]]: _description_
        """
        
        for _, value in self.entries():
            yield value
            
    def size(self) -> int:
        
        model_state_key = self.get_model_state_hash()
        return self.store.zcard(model_state_key)
    
    def empty(self) -> None:
        
        model_state_key = self.get_model_state_hash()
        
        buffer : Sequence[K] = []
        for _, key in self._keys():
            
            buffer.append(key) # fill up the buffer
            if len(buffer) >= self.buffer: # once it's full
                # dispatch the deletes
                self.store.zrem(model_state_key, *buffer) 
                self.store.delete(*buffer) 
        
        # empty the buffer one last time
        if len(buffer) > 0:
            print(buffer)
            self.store.zrem(model_state_key, *buffer) 
            self.store.delete(*buffer) 
        